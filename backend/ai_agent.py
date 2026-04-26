import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuração do Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

def extrair_dados_nota_fiscal(caminho_arquivo):
    """
    Usa o modelo Gemini para extrair informações de uma nota fiscal.
    """
    if not API_KEY:
        return {"erro": "GEMINI_API_KEY não configurada no arquivo .env"}

    try:
        # Carrega o modelo
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Lê o arquivo
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        # Determina o tipo mime com base na extensão
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        mime_type = "application/pdf" if extensao == ".pdf" else "image/jpeg"

        prompt = """
        Você é um especialista em leitura de Notas Fiscais brasileiras. 
        Analise o documento anexo e extraia as seguintes informações no formato JSON:
        
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

        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": conteudo
            }
        ])

        # Limpa a resposta para garantir que seja um JSON válido
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text_response)

    except Exception as e:
        return {"erro": f"Erro ao processar a nota fiscal: {str(e)}"}
