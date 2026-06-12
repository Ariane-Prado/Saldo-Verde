import os
import logging
import numpy as np
import faiss
from google import genai
from google.genai import types
from dotenv import load_dotenv
import database
import config

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_EMBED_MODEL = "models/gemini-embedding-2"
_EMBED_DIM = 3072

gemini_client = None

# ── Banco vetorial em memória (FAISS) ─────────────────────────────────────────

_vector_store = None  # {"index": faiss.Index, "textos_completos": [...], "total": int}


def _get_gemini_client():
    global gemini_client
    chave = config.get_gemini_key() or GEMINI_API_KEY
    if gemini_client is None and chave:
        gemini_client = genai.Client(
            api_key=chave,
            http_options={"api_version": "v1"}
        )
    return gemini_client


# ── Banco de dados ─────────────────────────────────────────────────────────────

def _buscar_registros(limit=20):
    conn = database.get_connection()
    cur = conn.cursor()
    limite_sql = f"LIMIT {limit}" if limit else ""
    cur.execute(f"""
        SELECT
            m.id,
            m.tipo,
            m.valor_total,
            m.data_emissao,
            forn.razao_social AS fornecedor,
            fat.razao_social  AS faturado,
            cl.descricao      AS classificacao,
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
    registros = [dict(zip(colunas, linha)) for linha in cur.fetchall()]
    cur.close()
    conn.close()
    return registros


def _formatar_linha(r):
    return (
        f"Movimento #{r.get('id')} | {r.get('tipo') or '-'} | "
        f"Fornecedor: {r.get('fornecedor') or '-'} | "
        f"Faturado: {r.get('faturado') or '-'} | "
        f"Classificação: {r.get('classificacao') or '-'} | "
        f"Total: R$ {r.get('valor_total') or '-'} | "
        f"Emissão: {r.get('data_emissao') or '-'} | "
        f"Parcela: {r.get('identificacao') or '-'} | "
        f"Venc: {r.get('data_vencimento') or '-'} | "
        f"R$ {r.get('valor_parcela') or '-'}"
    )


def _formatar_para_embedding(r):
    # Apenas a classificação — campo semanticamente relevante para busca
    return r.get('classificacao') or '-'


# ── Geração de embeddings ──────────────────────────────────────────────────────

def _embed_textos(textos, chunk_size=100):
    """Vetoriza uma lista de textos. Retorna array (N, DIM)."""
    client = _get_gemini_client()
    vetores = []
    for i in range(0, len(textos), chunk_size):
        chunk = textos[i:i + chunk_size]
        result = client.models.embed_content(
            model=_EMBED_MODEL,
            contents=chunk,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
        )
        vetores.extend(np.array(e.values, dtype=np.float32) for e in result.embeddings)
    return np.array(vetores, dtype=np.float32)


def _embed_query(texto):
    """Vetoriza a pergunta do usuário. Retorna array (1, DIM)."""
    client = _get_gemini_client()
    result = client.models.embed_content(
        model=_EMBED_MODEL,
        contents=texto,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
    )
    return np.array(result.embeddings[0].values, dtype=np.float32).reshape(1, -1)


# ── Banco vetorial FAISS ───────────────────────────────────────────────────────

def _build_vector_store():
    """
    Vetorização de Dados → Banco Vetorial (FAISS)
    Carrega todos os registros, gera embeddings e indexa no FAISS.
    Chamado uma vez por sessão.
    """
    global _vector_store
    logger.info("[FAISS] Construindo índice vetorial...")

    registros = _buscar_registros(limit=None)
    if not registros:
        return None

    textos_completos = [_formatar_linha(r) for r in registros]
    textos_embedding = [_formatar_para_embedding(r) for r in registros]

    # Vetorização: texto → embedding (representação numérica semântica)
    vetores = _embed_textos(textos_embedding)

    # Normaliza para Inner Product = cosine similarity
    faiss.normalize_L2(vetores)

    # Cria índice FAISS (Inner Product sobre vetores normalizados = cosine similarity)
    index = faiss.IndexFlatIP(_EMBED_DIM)
    index.add(vetores)

    _vector_store = {
        "index": index,
        "textos_completos": textos_completos,
        "total": len(registros),
    }
    logger.info(f"[FAISS] Índice construído com {len(registros)} documentos.")
    return _vector_store


def reset_vector_store():
    """Invalida o índice — chame após inserir/atualizar registros no banco."""
    global _vector_store
    _vector_store = None
    logger.info("[FAISS] Índice vetorial invalidado.")


def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        _build_vector_store()
    return _vector_store


# ── Recuperação semântica ──────────────────────────────────────────────────────

def _recuperar_contexto(pergunta, top_k=15):
    """
    Fluxo RAG — Recuperação:
    1. Embed da query
    2. Busca por similaridade no FAISS
    3. Retorna os top_k documentos mais semânticos
    """
    store = _get_vector_store()
    if store is None:
        return None

    vetor_query = _embed_query(pergunta)
    faiss.normalize_L2(vetor_query)

    scores, indices = store["index"].search(vetor_query, top_k)

    # Filtra resultados inválidos (FAISS retorna -FLT_MAX quando vetor é zero/NaN)
    # e deduplica movimentos (o JOIN gera múltiplas linhas por parcela)
    vistos = set()
    resultado = []
    logger.info("[RANKING] top classificações recuperadas:")
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
        if score < -1.0:
            continue
        texto = store["textos_completos"][idx]
        if texto in vistos:
            continue
        vistos.add(texto)
        resultado.append(texto)
        logger.info(f"  #{rank+1} score={score:.4f} | {texto[:80]}")

    return "\n".join(resultado) if resultado else None


# ── LLM ───────────────────────────────────────────────────────────────────────

def _chamar_llm(contexto, pergunta):
    """
    Prompt Enriquecido = Pergunta + Contexto Recuperado → LLM
    """
    client = _get_gemini_client()
    prompt = (
        "Você é um assistente de gestão financeira agrícola. "
        "Os dados abaixo são os registros financeiros mais relevantes para a pergunta. "
        "Responda com base nesses dados interpretando a pergunta semanticamente: "
        "a pergunta pode usar termos diferentes dos nomes exatos das classificações. "
        "Por exemplo, 'máquinas e equipamentos' engloba classificações como "
        "'MANUTENÇÃO DE MÁQUINAS' e 'AQUISIÇÃO DE EQUIPAMENTOS'. "
        "Seja objetivo e claro. Se realmente não houver dados relevantes, diga isso.\n\n"
        f"DADOS RELEVANTES:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    return response.text


# ── Endpoints públicos ─────────────────────────────────────────────────────────

def consultar_rag_simples(pergunta):
    registros = _buscar_registros()
    if not registros:
        return "Nenhum registro encontrado no banco de dados."
    contexto = "\n".join(_formatar_linha(r) for r in registros)
    return _chamar_llm(contexto, pergunta)


def consultar_rag_embeddings(pergunta, top_k=15):
    """
    RAG completo:
    1. Recupera contexto semântico via FAISS
    2. Injeta no prompt
    3. LLM gera resposta fundamentada
    """
    contexto = _recuperar_contexto(pergunta, top_k=top_k)
    if contexto is None:
        return "Nenhum registro encontrado no banco de dados."
    return _chamar_llm(contexto, pergunta)
