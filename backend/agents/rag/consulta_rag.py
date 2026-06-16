import json
import logging
import os
import re
import threading
from dataclasses import dataclass, field

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

import config
import database

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Constantes e configuração ──────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_EMBED_MODEL        = "models/gemini-embedding-2"
_EMBED_DIM          = 3072
_SCORE_THRESHOLD    = 0.15        # cosine similarity mínimo aceitável
_MAX_CONTEXT_CHARS  = 40_000      # ~10k tokens — seguro para Gemini 2.5 Flash

_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
_META_PATH  = os.path.join(os.path.dirname(__file__), "faiss_meta.json")

_KEYWORDS_AGREGACAO = [
    "total", "soma", "quanto", "maior", "menor", "média", "quantos",
    "qual o valor", "qual foi", "qual é a despesa", "vencerão", "vencimento",
    "ranking", "segundo maior", "top",
    "mais alto", "mais baixo", "mais caro", "mais barato",
    "maior valor", "menor valor", "valor mais", "nota mais",
    "mais alta", "mais cara",
]

_KEYWORDS_SEMANTICO = [
    "semelhante", "parecido", "relacionado", "se destina", "finalidade",
    "pragas", "doenças", "corretivos", "neutralizadores", "tipo de",
    "para que serve", "utilizado para", "itens",
]

# ── Cliente Gemini ─────────────────────────────────────────────────────────────

gemini_client = None


def _get_gemini_client():
    global gemini_client
    chave = config.get_gemini_key() or GEMINI_API_KEY
    if gemini_client is None and chave:
        gemini_client = genai.Client(
            api_key=chave,
            http_options={"api_version": "v1"},
        )
    return gemini_client


# ── Extração de entidades ──────────────────────────────────────────────────────

@dataclass
class Entidades:
    ano: int | None = None
    documento: str | None = None          # CPF ou CNPJ formatado
    nome_entidade: str | None = None      # nome de pessoa/empresa
    classificacao_mencionada: str | None = None
    eh_agregacao: bool = False
    eh_semantico: bool = False


# Cache de categorias do banco — carregado na primeira extração
_categorias_cache: list[str] = []
_categorias_lock = threading.Lock()


def _carregar_categorias() -> list[str]:
    global _categorias_cache
    with _categorias_lock:
        if _categorias_cache:
            return _categorias_cache
        conn = database.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT descricao FROM CLASSIFICACAO WHERE ativo = TRUE ORDER BY descricao"
                )
                _categorias_cache = [row[0] for row in cur.fetchall() if row[0]]
        finally:
            conn.close()
    logger.info(f"[ENTIDADES] Categorias carregadas: {_categorias_cache}")
    return _categorias_cache


def _extrair_entidades(pergunta: str) -> Entidades:
    p = pergunta.lower()
    ent = Entidades()

    # Ano
    m = re.search(r'\b(20\d{2})\b', pergunta)
    if m:
        ent.ano = int(m.group(1))

    # CPF
    m = re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}', pergunta)
    if m:
        ent.documento = m.group()
    else:
        # CNPJ
        m = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', pergunta)
        if m:
            ent.documento = m.group()

    # Nome de entidade após gatilho relacional específico (sem "de"/"do" que são genéricos demais)
    m = re.search(
        r'(?:fornecedor|faturado|empresa|para)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]{3,40}?)(?:\s*\(|,|\.|$)',
        pergunta,
        re.IGNORECASE,
    )
    if m:
        candidato = m.group(1).strip()
        if len(candidato) >= 4 and not candidato.isdigit():
            ent.nome_entidade = candidato

    # Classificação mencionada — busca substring case-insensitive
    categorias = _carregar_categorias()
    for cat in categorias:
        if cat.lower() in p:
            ent.classificacao_mencionada = cat
            break

    # Sinais de intenção
    ent.eh_agregacao = any(kw in p for kw in _KEYWORDS_AGREGACAO)
    ent.eh_semantico = any(kw in p for kw in _KEYWORDS_SEMANTICO)

    logger.info(f"[ENTIDADES] {ent}")
    return ent


# ── Banco de dados ─────────────────────────────────────────────────────────────

def _contar_movimentos() -> int:
    conn = database.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM MOVIMENTOCONTAS WHERE ativo = TRUE")
            return cur.fetchone()[0]
    finally:
        conn.close()


def _buscar_registros(limit: int | None = 20) -> list[dict]:
    conn = database.get_connection()
    try:
        with conn.cursor() as cur:
            limite_sql = f"LIMIT {int(limit)}" if limit else ""
            cur.execute(f"""
                SELECT
                    m.id, m.tipo, m.valor_total, m.data_emissao,
                    forn.razao_social AS fornecedor,
                    fat.razao_social  AS faturado,
                    cl.descricao      AS classificacao,
                    m.descricao_itens,
                    p.identificacao,
                    p.data_vencimento,
                    p.valor           AS valor_parcela
                FROM MOVIMENTOCONTAS m
                LEFT JOIN PESSOAS forn     ON forn.id = m.id_fornecedor
                LEFT JOIN PESSOAS fat      ON fat.id  = m.id_faturado
                LEFT JOIN CLASSIFICACAO cl ON cl.id   = m.id_classificacao
                LEFT JOIN PARCELACONTAS p  ON p.id_movimento = m.id
                WHERE m.ativo = TRUE
                ORDER BY m.data_emissao DESC
                {limite_sql}
            """)
            colunas = [desc[0] for desc in cur.description]
            return [dict(zip(colunas, linha)) for linha in cur.fetchall()]
    finally:
        conn.close()


def _buscar_ids_filtrados(entidades: Entidades) -> set[int]:
    """Retorna IDs de movimentos que satisfazem os filtros objetivos da pergunta."""
    conds: list[str] = ["m.ativo = TRUE"]
    params: list = []

    if entidades.ano:
        conds.append("EXTRACT(YEAR FROM m.data_emissao) = %s")
        params.append(entidades.ano)
    if entidades.documento:
        conds.append("(forn.cpf_cnpj = %s OR fat.cpf_cnpj = %s)")
        params.extend([entidades.documento, entidades.documento])
    if entidades.classificacao_mencionada:
        conds.append("cl.descricao ILIKE %s")
        params.append(f"%{entidades.classificacao_mencionada}%")
    if entidades.nome_entidade:
        conds.append("(forn.razao_social ILIKE %s OR fat.razao_social ILIKE %s)")
        params.extend([f"%{entidades.nome_entidade}%", f"%{entidades.nome_entidade}%"])

    # Sem filtros objetivos → sem restrição
    if len(conds) == 1:
        return set()

    where = " AND ".join(conds)
    conn = database.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT DISTINCT m.id
                FROM MOVIMENTOCONTAS m
                LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                LEFT JOIN CLASSIFICACAO cl ON cl.id = m.id_classificacao
                WHERE {where}
            """, params)
            ids = {row[0] for row in cur.fetchall()}
    finally:
        conn.close()

    logger.info(f"[PREFILTER] {len(ids)} movimentos encontrados para filtros: ano={entidades.ano}, "
                f"doc={entidades.documento}, class={entidades.classificacao_mencionada}, "
                f"nome={entidades.nome_entidade}")
    return ids


def _formatar_linha(r: dict) -> str:
    total = f"R$ {r['valor_total']}" if r.get("valor_total") is not None else "(já contabilizado)"
    return (
        f"Movimento #{r.get('id')} | {r.get('tipo') or '-'} | "
        f"Fornecedor: {r.get('fornecedor') or '-'} | "
        f"Faturado: {r.get('faturado') or '-'} | "
        f"Classificação: {r.get('classificacao') or '-'} | "
        f"Itens: {r.get('descricao_itens') or '-'} | "
        f"Total: {total} | "
        f"Emissão: {r.get('data_emissao') or '-'} | "
        f"Parcela: {r.get('identificacao') or '-'} | "
        f"Venc: {r.get('data_vencimento') or '-'} | "
        f"R$ {r.get('valor_parcela') or '-'}"
    )


def _formatar_para_embedding(r: dict) -> str:
    """Texto rico para indexação — todos os campos semanticamente relevantes."""
    return (
        f"Nota fiscal tipo {r.get('tipo') or 'APAGAR'}. "
        f"Fornecedor: {r.get('fornecedor') or 'desconhecido'}. "
        f"Faturado para: {r.get('faturado') or 'desconhecido'}. "
        f"Classificação: {r.get('classificacao') or 'sem classificação'}. "
        f"Itens/produtos: {r.get('descricao_itens') or 'não informado'}. "
        f"Valor total: R$ {r.get('valor_total') or '0'}. "
        f"Emitida em {r.get('data_emissao') or 'data desconhecida'}. "
        f"Parcela {r.get('identificacao') or '-'} "
        f"vencendo em {r.get('data_vencimento') or '-'} "
        f"no valor de R$ {r.get('valor_parcela') or '0'}."
    )


def _buscar_contexto_agregado(pergunta: str, entidades: Entidades) -> str:
    """
    Para perguntas de agregação: executa os cálculos no SQL e devolve
    um texto já consolidado. O LLM recebe resultados prontos, não dados brutos.
    """
    p = pergunta.lower()
    sobre_parcelas = any(
        t in p
        for t in ["vencerão", "vencem", "vencimento", "parcelas futuras", "parcela", "parcelas"]
    )

    cond_mov: list[str] = ["m.ativo = TRUE"]
    par_mov: list = []
    if entidades.ano:
        cond_mov.append("EXTRACT(YEAR FROM m.data_emissao) = %s")
        par_mov.append(entidades.ano)
    if entidades.documento:
        cond_mov.append("(forn.cpf_cnpj = %s OR fat.cpf_cnpj = %s)")
        par_mov.extend([entidades.documento, entidades.documento])
    where_mov = " AND ".join(cond_mov)

    periodo = f"ano {entidades.ano}" if entidades.ano else "todo o período"
    partes: list[str] = []

    conn = database.get_connection()
    try:
        with conn.cursor() as cur:
            if sobre_parcelas:
                cond_parc: list[str] = ["m.ativo = TRUE", "p.ativo = TRUE"]
                par_parc: list = []
                if entidades.ano:
                    cond_parc.append("EXTRACT(YEAR FROM p.data_vencimento) = %s")
                    par_parc.append(entidades.ano)
                if entidades.documento:
                    cond_parc.append("(forn.cpf_cnpj = %s OR fat.cpf_cnpj = %s)")
                    par_parc.extend([entidades.documento, entidades.documento])
                where_parc = " AND ".join(cond_parc)
                label_parc = f"com vencimento em {entidades.ano}" if entidades.ano else "no período consultado"

                cur.execute(f"""
                    SELECT fat.razao_social, fat.cpf_cnpj,
                           ROUND(SUM(p.valor)::NUMERIC, 2), COUNT(*)
                    FROM PARCELACONTAS p
                    JOIN MOVIMENTOCONTAS m ON m.id = p.id_movimento
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    WHERE {where_parc}
                    GROUP BY fat.razao_social, fat.cpf_cnpj
                    ORDER BY 3 DESC
                """, par_parc)
                partes.append(f"Parcelas {label_parc}:")
                rows = cur.fetchall()
                if rows:
                    for razao, cpf, tot, qtd in rows:
                        partes.append(f"  {razao or '-'} ({cpf or '-'}): R$ {tot} — {qtd} parcelas")
                else:
                    partes.append("  Nenhuma parcela encontrada para os filtros informados.")

                cur.execute(f"""
                    SELECT cl.descricao, ROUND(SUM(p.valor)::NUMERIC, 2), COUNT(*)
                    FROM PARCELACONTAS p
                    JOIN MOVIMENTOCONTAS m ON m.id = p.id_movimento
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    LEFT JOIN CLASSIFICACAO cl ON cl.id = m.id_classificacao
                    WHERE {where_parc}
                    GROUP BY cl.descricao
                    ORDER BY 2 DESC
                """, par_parc)
                partes.append(f"\nPor classificação ({label_parc}):")
                for desc, tot, qtd in cur.fetchall():
                    partes.append(f"  {desc or '-'}: R$ {tot} ({qtd} parcelas)")

            else:
                # Total geral
                cur.execute(f"""
                    SELECT ROUND(SUM(m.valor_total)::NUMERIC, 2)
                    FROM MOVIMENTOCONTAS m
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    WHERE {where_mov}
                """, par_mov)
                total_geral = cur.fetchone()[0]
                partes.append(f"TOTAL GERAL de NFs emitidas ({periodo}): R$ {total_geral}")

                # Por fornecedor
                cur.execute(f"""
                    SELECT forn.razao_social, ROUND(SUM(m.valor_total)::NUMERIC, 2), COUNT(*)
                    FROM MOVIMENTOCONTAS m
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    WHERE {where_mov}
                    GROUP BY forn.razao_social
                    ORDER BY 2 DESC
                """, par_mov)
                partes.append(f"\nTotal por fornecedor ({periodo}):")
                for razao, tot, qtd in cur.fetchall():
                    partes.append(f"  {razao or '-'}: R$ {tot} ({qtd} NFs)")

                # Por classificação
                cur.execute(f"""
                    SELECT cl.descricao, ROUND(SUM(m.valor_total)::NUMERIC, 2), COUNT(*)
                    FROM MOVIMENTOCONTAS m
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    LEFT JOIN CLASSIFICACAO cl ON cl.id = m.id_classificacao
                    WHERE {where_mov}
                    GROUP BY cl.descricao
                    ORDER BY 2 DESC
                """, par_mov)
                partes.append(f"\nTotal por classificação ({periodo}):")
                for desc, tot, qtd in cur.fetchall():
                    partes.append(f"  {desc or '-'}: R$ {tot} ({qtd} NFs)")

                # Maior NF individual (ranking completo para suportar "segundo maior" etc.)
                cur.execute(f"""
                    SELECT m.id, forn.razao_social, cl.descricao, m.valor_total, m.data_emissao
                    FROM MOVIMENTOCONTAS m
                    LEFT JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                    LEFT JOIN PESSOAS fat  ON fat.id  = m.id_faturado
                    LEFT JOIN CLASSIFICACAO cl ON cl.id = m.id_classificacao
                    WHERE {where_mov}
                    ORDER BY m.valor_total DESC
                    LIMIT 5
                """, par_mov)
                rows = cur.fetchall()
                if rows:
                    partes.append(f"\nTop-5 maiores NFs individuais ({periodo}):")
                    for i, row in enumerate(rows, 1):
                        partes.append(
                            f"  #{i}: Mov#{row[0]} | {row[1] or '-'} | {row[2] or '-'} | "
                            f"R$ {row[3]} | {row[4]}"
                        )
    finally:
        conn.close()

    logger.info(f"[AGREGADO] contexto gerado — entidades: {entidades}")
    return "\n".join(partes)


# ── Geração de embeddings ──────────────────────────────────────────────────────

def _embed_textos(textos: list[str], chunk_size: int = 100) -> np.ndarray:
    client = _get_gemini_client()
    vetores = []
    for i in range(0, len(textos), chunk_size):
        chunk = textos[i : i + chunk_size]
        result = client.models.embed_content(
            model=_EMBED_MODEL,
            contents=chunk,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        vetores.extend(np.array(e.values, dtype=np.float32) for e in result.embeddings)
    return np.array(vetores, dtype=np.float32)


def _embed_query(texto: str) -> np.ndarray:
    client = _get_gemini_client()
    result = client.models.embed_content(
        model=_EMBED_MODEL,
        contents=texto,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return np.array(result.embeddings[0].values, dtype=np.float32).reshape(1, -1)


# ── Banco vetorial FAISS ───────────────────────────────────────────────────────

_vector_store = None  # {"index": faiss.Index, "textos_completos": [...], "mov_ids": [...], "total": int}
_build_lock   = threading.Lock()


def _salvar_indice(index: faiss.Index, textos: list[str], mov_ids: list[int], total: int) -> None:
    faiss.write_index(index, _INDEX_PATH)
    with open(_META_PATH, "w", encoding="utf-8") as f:
        json.dump({"textos_completos": textos, "mov_ids": mov_ids, "total": total}, f, ensure_ascii=False)
    logger.info(f"[FAISS] Índice salvo em disco ({total} movimentos).")


def _carregar_indice() -> dict | None:
    if not (os.path.exists(_INDEX_PATH) and os.path.exists(_META_PATH)):
        return None
    try:
        index = faiss.read_index(_INDEX_PATH)
        with open(_META_PATH, encoding="utf-8") as f:
            meta = json.load(f)
        logger.info(f"[FAISS] Índice carregado do disco ({meta['total']} movimentos).")
        return {
            "index": index,
            "textos_completos": meta["textos_completos"],
            "mov_ids": meta.get("mov_ids", []),
            "total": meta["total"],
        }
    except Exception as e:
        logger.warning(f"[FAISS] Falha ao carregar índice do disco: {e}. Reconstruindo.")
        return None


def _build_vector_store_interno() -> dict | None:
    global _vector_store
    logger.info("[FAISS] Construindo índice vetorial...")

    registros = _buscar_registros(limit=None)
    if not registros:
        return None

    # Deduplica por movimento (JOIN pode gerar múltiplas linhas por parcela)
    vistos: set[int] = set()
    movimentos_unicos = []
    for r in registros:
        if r["id"] not in vistos:
            vistos.add(r["id"])
            movimentos_unicos.append(r)

    textos_completos  = [_formatar_linha(r) for r in movimentos_unicos]
    textos_embedding  = [_formatar_para_embedding(r) for r in movimentos_unicos]
    mov_ids           = [r["id"] for r in movimentos_unicos]

    vetores = _embed_textos(textos_embedding)
    faiss.normalize_L2(vetores)

    index = faiss.IndexFlatIP(_EMBED_DIM)
    index.add(vetores)

    store = {
        "index": index,
        "textos_completos": textos_completos,
        "mov_ids": mov_ids,
        "total": len(registros),
    }
    _salvar_indice(index, textos_completos, mov_ids, len(registros))
    logger.info(
        f"[FAISS] Índice construído com {len(movimentos_unicos)} movimentos únicos "
        f"(de {len(registros)} linhas)."
    )
    return store


def _get_vector_store() -> dict | None:
    global _vector_store
    if _vector_store is not None:
        total_db = _contar_movimentos()
        if total_db != len(_vector_store.get("mov_ids", [])):
            logger.info(f"[FAISS] Índice desatualizado ({len(_vector_store.get('mov_ids', []))} vs {total_db} no banco) — reconstruindo.")
            _vector_store = None
        else:
            return _vector_store
    with _build_lock:
        if _vector_store is None:
            store = _carregar_indice()
            if store is not None:
                total_db = _contar_movimentos()
                if total_db != len(store.get("mov_ids", [])):
                    logger.info("[FAISS] Índice em disco desatualizado — reconstruindo.")
                    store = None
            _vector_store = store if store is not None else _build_vector_store_interno()
    return _vector_store


def reset_vector_store() -> None:
    """Invalida o índice em memória e apaga arquivos em disco. Chame após inserir/atualizar registros."""
    global _vector_store
    _vector_store = None
    for path in (_INDEX_PATH, _META_PATH):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            logger.warning(f"[FAISS] Não foi possível remover {path}: {e}")
    logger.info("[FAISS] Índice vetorial invalidado.")


# ── Busca semântica ────────────────────────────────────────────────────────────

def _recuperar_contexto_faiss(
    pergunta: str,
    top_k: int = 30,
    subset_ids: set[int] | None = None,
) -> str | None:
    """
    Recupera os top_k documentos mais semanticamente próximos da pergunta.
    Se subset_ids não-vazio, restringe a busca a esses IDs de movimentos.
    """
    store = _get_vector_store()
    if store is None:
        return None

    vetor_query = _embed_query(pergunta)
    faiss.normalize_L2(vetor_query)

    # Busca com margem extra para compensar filtragem por subset
    busca_k = top_k * 3 if subset_ids else top_k
    busca_k = min(busca_k, store["index"].ntotal)

    scores, indices = store["index"].search(vetor_query, busca_k)

    resultado: list[str] = []
    logger.info("[RANKING] top classificações recuperadas:")
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
        if score < _SCORE_THRESHOLD:
            break  # FAISS retorna em ordem decrescente — todos os seguintes serão piores
        if idx < 0 or idx >= len(store["textos_completos"]):
            continue
        # Filtra por subset de IDs se pré-filtro SQL foi aplicado
        if subset_ids:
            mov_id = store["mov_ids"][idx] if idx < len(store["mov_ids"]) else None
            if mov_id not in subset_ids:
                continue
        texto = store["textos_completos"][idx]
        resultado.append(texto)
        logger.info(f"  #{rank+1} score={score:.4f} | {texto[:80]}")
        if len(resultado) >= top_k:
            break

    return "\n".join(resultado) if resultado else None


# ── Controle de contexto ───────────────────────────────────────────────────────

def _truncar_contexto(texto: str) -> str:
    if len(texto) <= _MAX_CONTEXT_CHARS:
        return texto
    logger.warning(f"[CONTEXTO] Truncado: {len(texto)} → {_MAX_CONTEXT_CHARS} chars")
    linhas, acc = [], 0
    for linha in texto.split("\n"):
        if acc + len(linha) > _MAX_CONTEXT_CHARS:
            break
        linhas.append(linha)
        acc += len(linha) + 1
    return "\n".join(linhas)


# ── LLM ───────────────────────────────────────────────────────────────────────

def _chamar_llm(contexto: str, pergunta: str, modo: str = "agregacao") -> str:
    client = _get_gemini_client()
    contexto = _truncar_contexto(contexto)

    if modo == "semantico":
        instrucao = (
            "Os dados abaixo são registros financeiros. "
            "Analise todos os campos: nome do fornecedor, faturado, classificação, valor e datas. "
            "Identifique e descreva os registros que se enquadram na pergunta, considerando sinônimos e termos relacionados. "
            "Não calcule totais nem faça rankings a menos que a pergunta peça explicitamente. "
            "Se não houver registros relevantes, diga isso claramente."
        )
    else:
        instrucao = (
            "Os dados abaixo são TODOS os registros financeiros correspondentes à sua consulta. "
            "Calcule totais, somas e identifique maior/menor valor diretamente a partir deles. "
            "Interprete a pergunta semanticamente: termos diferentes podem se referir à mesma categoria. "
            "Seja objetivo e claro. Se não houver dados relevantes, diga isso."
        )

    prompt = (
        f"Você é um assistente de gestão financeira agrícola. {instrucao}\n\n"
        f"DADOS:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
    )
    return response.text


# ── API pública ────────────────────────────────────────────────────────────────

def consultar_rag_simples(pergunta: str) -> str:
    """
    RAG Simples — SQL-first.
    Sempre passa pelo caminho de agregação SQL. O LLM interpreta e formata
    os resultados prontos, sem precisar calcular nada.
    Se não houver filtros nem sinais de agregação, envia os registros mais
    recentes como contexto (mantém comportamento original para perguntas abertas).
    """
    entidades = _extrair_entidades(pergunta)

    if entidades.eh_agregacao or entidades.documento or entidades.ano:
        contexto = _buscar_contexto_agregado(pergunta, entidades)
        if not contexto:
            return "Nenhum registro encontrado no banco de dados."
        return _chamar_llm(contexto, pergunta, modo="agregacao")

    # Fallback: todos os registros sem embedding
    registros = _buscar_registros(limit=None)
    if not registros:
        return "Nenhum registro encontrado no banco de dados."

    vistos: set[int] = set()
    linhas: list[str] = []
    for r in registros:
        if r["id"] not in vistos:
            vistos.add(r["id"])
            linhas.append(_formatar_linha(r))

    contexto = _truncar_contexto("\n".join(linhas))
    return _chamar_llm(contexto, pergunta, modo="semantico")


def consultar_rag_embeddings(pergunta: str, top_k: int = 30) -> str:
    """
    RAG Semântico — com lógica híbrida interna.

    Roteamento automático:
    1. Agregação / filtros estruturados  → SQL pré-agregado (modo simples interno)
    2. Semântico com filtros objetivos   → pré-filtro SQL + FAISS sobre subset
    3. Semântico puro                    → FAISS global (top_k movimentos únicos)
    """
    entidades = _extrair_entidades(pergunta)

    # Caso 1: pergunta puramente agregada (total, soma, ranking) sem sinal semântico
    if entidades.eh_agregacao and not entidades.eh_semantico:
        logger.info("[RAG-SEM] Modo agregação SQL")
        contexto = _buscar_contexto_agregado(pergunta, entidades)
        if not contexto:
            return "Nenhum registro encontrado no banco de dados."
        return _chamar_llm(contexto, pergunta, modo="agregacao")

    # Caso 2: sinal semântico presente — pode ter pré-filtro SQL ou não
    tem_filtros_objetivos = bool(
        entidades.ano
        or entidades.documento
        or entidades.classificacao_mencionada
        or entidades.nome_entidade
    )

    subset_ids: set[int] = set()
    contexto_sql_extra = ""

    if tem_filtros_objetivos:
        logger.info("[RAG-SEM] Modo híbrido interno — pré-filtro SQL + FAISS")
        subset_ids = _buscar_ids_filtrados(entidades)

        # Se há sinal de agregação junto com semântico, inclui dados SQL como contexto adicional
        if entidades.eh_agregacao:
            contexto_sql_extra = _buscar_contexto_agregado(pergunta, entidades)
    else:
        logger.info("[RAG-SEM] Modo semântico puro — FAISS global")

    contexto_faiss = _recuperar_contexto_faiss(pergunta, top_k=top_k, subset_ids=subset_ids or None)

    if not contexto_faiss and not contexto_sql_extra:
        # Fallback: FAISS não encontrou nada — busca todos os registros do banco
        registros = _buscar_registros(limit=None)
        if not registros:
            return "Nenhum registro encontrado no banco de dados."
        vistos: set[int] = set()
        linhas: list[str] = []
        for r in registros:
            if r["id"] not in vistos:
                vistos.add(r["id"])
                linhas.append(_formatar_linha(r))
        contexto_faiss = _truncar_contexto("\n".join(linhas))

    partes: list[str] = []
    if contexto_sql_extra:
        partes.append("=== DADOS ESTRUTURADOS ===\n" + contexto_sql_extra)
    if contexto_faiss:
        partes.append("=== REGISTROS SEMANTICAMENTE RELEVANTES ===\n" + contexto_faiss)

    contexto = _truncar_contexto("\n\n".join(partes))
    return _chamar_llm(contexto, pergunta, modo="semantico")
