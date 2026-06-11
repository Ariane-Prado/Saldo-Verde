import os
import json
import base64
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
import pypdf
import config

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

gemini_client = None

def _get_gemini_client():
    global gemini_client
    chave = config.get_gemini_key() or GEMINI_API_KEY
    if gemini_client is None and chave:
        gemini_client = genai.Client(api_key=chave)
    return gemini_client

PROMPT = """
Você é um especialista em leitura de Notas Fiscais brasileiras e classificação de despesas agrícolas.

Analise o documento e extraia as informações abaixo. Além disso, interprete os produtos/serviços da nota e classifique a despesa conforme as categorias definidas.

Retorne APENAS o JSON abaixo, sem blocos de código ou explicações. Se não encontrar algum campo, deixe como null.

{
    "fornecedor": {
        "razao_social": "string",
        "fantasia": "string",
        "cnpj": "string"
    },
    "faturado": {
        "nome_completo": "string",
        "cpf": "string"
    },
    "numero_nota_fiscal": "string",
    "data_emissao": "string",
    "descricao_produtos": "string",
    "parcelas": [
        {
            "numero": 1,
            "data_vencimento": "string",
            "valor": float
        }
    ],
    "valor_total": float,
    "classificacao_despesa": [
        {
            "categoria": "string",
            "justificativa": "string"
        }
    ]
}

INSTRUÇÕES:
- "fornecedor" é quem emitiu a nota fiscal (vendedor/prestador).
- "faturado" é o destinatário da nota (comprador/contratante). Se for pessoa jurídica e não houver CPF, deixe cpf como null.
- "descricao_produtos" é um resumo textual dos produtos ou serviços da nota, sem necessidade de listar cada item separadamente.
- "parcelas" deve ter estrutura para múltiplas parcelas, mas por padrão use apenas uma parcela com a data de vencimento e valor total da nota. Se a data de vencimento não constar na nota, deixe como null.
- A classificação de despesa deve ser interpretada com base nos produtos/serviços, não extraída diretamente. Pode haver mais de uma classificação.
- Use apenas as categorias listadas abaixo, sem subcategorias.

CATEGORIAS DISPONÍVEIS:

- INSUMOS AGRÍCOLAS (sementes, fertilizantes, defensivos, corretivos)
- MANUTENÇÃO E OPERAÇÃO (combustíveis, lubrificantes, peças, manutenção de máquinas, pneus, ferramentas)
- RECURSOS HUMANOS (mão de obra, salários, encargos)
- SERVIÇOS OPERACIONAIS (frete, transporte, colheita terceirizada, secagem, armazenagem, pulverização)
- INFRAESTRUTURA E UTILIDADES (energia elétrica, arrendamento, construções, materiais de construção)
- ADMINISTRATIVAS (honorários contábeis, advocatícios, agronômicos, despesas bancárias)
- SEGUROS E PROTEÇÃO (seguro agrícola, seguro de ativos, seguro prestamista)
- IMPOSTOS E TAXAS (ITR, IPTU, IPVA, INCRA-CCIR)
- INVESTIMENTOS (aquisição de máquinas, veículos, imóveis, infraestrutura rural)

Exemplos de classificação:
- Compra de Óleo Diesel → categoria: "MANUTENÇÃO E OPERAÇÃO"
- Compra de Material Hidráulico → categoria: "INFRAESTRUTURA E UTILIDADES"
- Compra de Herbicida → categoria: "INSUMOS AGRÍCOLAS"
"""

def limpar_json(texto):
    texto = texto.strip()
    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()
    elif texto.startswith("```"):
        texto = texto.replace("```", "").strip()
    return texto

def extrair_com_gemini(caminho_arquivo):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    mime_type = "application/pdf" if extensao == ".pdf" else "image/jpeg"

    with open(caminho_arquivo, "rb") as f:
        conteudo = f.read()

    response = _get_gemini_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=[PROMPT, types.Part.from_bytes(data=conteudo, mime_type=mime_type)]
    )
    raw = limpar_json(response.text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini retornou JSON inválido: {e} | Resposta: {raw[:300]}")

def extrair_com_claude(caminho_arquivo):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    media_type = "application/pdf" if extensao == ".pdf" else "image/jpeg"

    with open(caminho_arquivo, "rb") as f:
        conteudo_base64 = base64.standard_b64encode(f.read()).decode("utf-8")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
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
    raw = limpar_json(message.content[0].text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude retornou JSON inválido: {e} | Resposta: {raw[:300]}")

def extrair_com_openai(caminho_arquivo):
    client = OpenAI(api_key=OPENAI_API_KEY)
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if extensao == ".pdf":
        with open(caminho_arquivo, "rb") as f:
            reader = pypdf.PdfReader(f)
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
    raw = limpar_json(response.choices[0].message.content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"OpenAI retornou JSON inválido: {e} | Resposta: {raw[:300]}")
