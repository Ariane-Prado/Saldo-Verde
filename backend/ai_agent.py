import os
import json
import base64
import google.generativeai as genai
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

PROMPT = """
Você é um especialista em leitura de Notas Fiscais brasileiras.
Analise o documento e extraia as seguintes informações no formato JSON:

{
    "emitente": {
        "nome_razao_social": "string",
        "cnpj": "string",
        "endereco": "string"
    },
    "destinatario": {
        "nome_razao_social": "string",
        "cnpj": "string"
    },
    "nota_fiscal": {
        "numero": "string",
        "serie": "string",
        "data_emissao": "string"
    },
    "valor_total": float,
    "itens": [
        {
            "descricao": "string",
            "quantidade": float,
            "valor_unitario": float,
            "valor_total": float
        }
    ]
}

Retorne APENAS o JSON, sem blocos de código ou explicações.
Se não encontrar algum campo, deixe como null.
"""

def limpar_json(texto):
    texto = texto.strip()
    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()
    elif texto.startswith("```"):
        texto = texto.replace("```", "").strip()
    return texto

def extrair_com_gemini(caminho_arquivo):
    model = genai.GenerativeModel("gemini-2.5-flash")
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    mime_type = "application/pdf" if extensao == ".pdf" else "image/jpeg"

    with open(caminho_arquivo, "rb") as f:
        conteudo = f.read()

    response = model.generate_content([
        PROMPT,
        {"mime_type": mime_type, "data": conteudo}
    ])
    return json.loads(limpar_json(response.text))

def extrair_com_claude(caminho_arquivo):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    media_type = "application/pdf" if extensao == ".pdf" else "image/jpeg"

    with open(caminho_arquivo, "rb") as f:
        conteudo_base64 = base64.standard_b64encode(f.read()).decode("utf-8")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": conteudo_base64,
                        },
                    },
                    {"type": "text", "text": PROMPT}
                ],
            }
        ],
    )
    return json.loads(limpar_json(message.content[0].text))

def extrair_com_openai(caminho_arquivo):
    client = OpenAI(api_key=OPENAI_API_KEY)
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if extensao == ".pdf":
        with open(caminho_arquivo, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            texto = "\n".join(
                page.extract_text() for page in reader.pages if page.extract_text()
            )
        conteudo_mensagem = f"{PROMPT}\n\nConteúdo do documento:\n{texto}"
        messages = [{"role": "user", "content": conteudo_mensagem}]
    else:
        with open(caminho_arquivo, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                ],
            }
        ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return json.loads(limpar_json(response.choices[0].message.content))

def extrair_dados_nota_fiscal(caminho_arquivo):
    if GEMINI_API_KEY:
        try:
            return extrair_com_gemini(caminho_arquivo)
        except Exception as e:
            print(f"[Gemini falhou] {e} — tentando Claude...")

    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "sua_chave_aqui":
        try:
            return extrair_com_claude(caminho_arquivo)
        except Exception as e:
            print(f"[Claude falhou] {e} — tentando OpenAI...")

    if OPENAI_API_KEY:
        try:
            return extrair_com_openai(caminho_arquivo)
        except Exception as e:
            return {"erro": f"Todas as APIs falharam. Último erro (OpenAI): {str(e)}"}

    return {"erro": "Nenhuma API disponível. Configure ao menos uma chave no .env"}
