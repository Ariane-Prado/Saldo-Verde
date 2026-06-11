import os
import re
import math
import numpy as np
from collections import Counter
from google import genai
from dotenv import load_dotenv
import database
import config

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None
gemini_embed_client = None

def _get_gemini_client():
    global gemini_client
    chave = config.get_gemini_key() or GEMINI_API_KEY
    if gemini_client is None and chave:
        gemini_client = genai.Client(api_key=chave)
    return gemini_client


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


# ── RAG Embeddings: vetorização TF local (bag-of-words + cosine similarity) ──

def _tokenizar(texto):
    return re.findall(r'\w+', texto.lower())

def _tf_vetor(texto):
    return Counter(_tokenizar(texto))

def _cosine_similarity_tf(v1, v2):
    comum = set(v1.keys()) & set(v2.keys())
    numerador = sum(v1[w] * v2[w] for w in comum)
    norma1 = math.sqrt(sum(c ** 2 for c in v1.values()))
    norma2 = math.sqrt(sum(c ** 2 for c in v2.values()))
    if not norma1 or not norma2:
        return 0.0
    return numerador / (norma1 * norma2)


def consultar_rag_simples(pergunta):
    registros = _buscar_registros()
    if not registros:
        return "Nenhum registro encontrado no banco de dados."
    contexto = "\n".join(_formatar_linha(r) for r in registros)
    return _chamar_llm(contexto, pergunta)


def consultar_rag_embeddings(pergunta, top_k=5):
    registros = _buscar_registros(limit=None)
    if not registros:
        return "Nenhum registro encontrado no banco de dados."

    textos = [_formatar_linha(r) for r in registros]

    # Vetoriza cada registro e a pergunta (TF bag-of-words)
    vetor_pergunta = _tf_vetor(pergunta)
    scores = [_cosine_similarity_tf(vetor_pergunta, _tf_vetor(t)) for t in textos]

    # Seleciona os top_k registros mais similares à pergunta
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    contexto = "\n".join(textos[i] for i in top_indices)

    return _chamar_llm(contexto, pergunta)
