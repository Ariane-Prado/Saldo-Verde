import os
import json
import base64
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
import pypdf

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

gemini_client = None

def _get_gemini_client():
    global gemini_client
    if gemini_client is None and GEMINI_API_KEY:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
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
            "subcategoria": "string",
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

CATEGORIAS E SUBCATEGORIAS DISPONÍVEIS:

- INSUMOS AGRÍCOLAS: Sementes | Fertilizantes | Defensivos Agrícolas | Corretivos
- MANUTENÇÃO E OPERAÇÃO: Combustíveis e Lubrificantes | Peças e Componentes Mecânicos | Manutenção de Máquinas e Equipamentos | Pneus, Filtros e Correias | Ferramentas e Utensílios
- RECURSOS HUMANOS: Mão de Obra Temporária | Salários e Encargos
- SERVIÇOS OPERACIONAIS: Frete e Transporte | Colheita Terceirizada | Secagem e Armazenagem | Pulverização e Aplicação
- INFRAESTRUTURA E UTILIDADES: Energia Elétrica | Arrendamento de Terras | Construções e Reformas | Materiais de Construção
- ADMINISTRATIVAS: Honorários Contábeis, Advocatícios ou Agronômicos | Despesas Bancárias e Financeiras
- SEGUROS E PROTEÇÃO: Seguro Agrícola | Seguro de Ativos (Máquinas/Veículos) | Seguro Prestamista
- IMPOSTOS E TAXAS: ITR | IPTU | IPVA | INCRA-CCIR
- INVESTIMENTOS: Aquisição de Máquinas e Implementos | Aquisição de Veículos | Aquisição de Imóveis | Infraestrutura Rural

Exemplos de classificação:
- Compra de Óleo Diesel → categoria: "MANUTENÇÃO E OPERAÇÃO", subcategoria: "Combustíveis e Lubrificantes"
- Compra de Material Hidráulico → categoria: "INFRAESTRUTURA E UTILIDADES", subcategoria: "Materiais de Construção"
- Compra de Herbicida → categoria: "INSUMOS AGRÍCOLAS", subcategoria: "Defensivos Agrícolas"
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
    return json.loads(limpar_json(response.text))

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
    return json.loads(limpar_json(message.content[0].text))

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
    return json.loads(limpar_json(response.choices[0].message.content))
