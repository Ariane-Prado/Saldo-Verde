import os
import numpy as np
from google import genai
from dotenv import load_dotenv
import database
import config

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None

def _get_gemini_client():
    global gemini_client
    chave = config.get_gemini_key() or GEMINI_API_KEY
    if gemini_client is None and chave:
        gemini_client = genai.Client(api_key=chave)
    return gemini_client


def _buscar_registros():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("""
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
        LIMIT 20
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


def _chamar_llm(contexto, pergunta):
    client = _get_gemini_client()
    prompt = (
        "Você é um assistente de gestão financeira agrícola. "
        "Responda apenas com base nos dados fornecidos abaixo. "
        "Seja objetivo e claro. Se não houver dados suficientes, diga isso.\n\n"
        f"DADOS DO SISTEMA:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    return response.text


def consultar_rag_simples(pergunta):
    registros = _buscar_registros()
    if not registros:
        return "Nenhum registro encontrado no banco de dados."
    contexto = "\n".join(_formatar_linha(r) for r in registros)
    return _chamar_llm(contexto, pergunta)


def consultar_rag_embeddings(pergunta, top_k=5):
    registros = _buscar_registros()
    if not registros:
        return "Nenhum registro encontrado no banco de dados."

    client = _get_gemini_client()
    textos = [_formatar_linha(r) for r in registros]

    # Gera embeddings dos registros (1 chamada batch)
    resp_docs = client.models.embed_content(
        model="text-embedding-004",
        contents=textos
    )
    vetores_docs = [e.values for e in resp_docs.embeddings]

    # Gera embedding da pergunta
    resp_query = client.models.embed_content(
        model="text-embedding-004",
        contents=[pergunta]
    )
    vetor_pergunta = resp_query.embeddings[0].values

    # Calcula cosine similarity
    vp = np.array(vetor_pergunta)
    scores = []
    for vd in vetores_docs:
        vd_arr = np.array(vd)
        score = float(np.dot(vp, vd_arr) / (np.linalg.norm(vp) * np.linalg.norm(vd_arr)))
        scores.append(score)

    # Pega os top_k índices mais relevantes
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    contexto = "\n".join(textos[i] for i in top_indices)

    return _chamar_llm(contexto, pergunta)
