from agents.nota_fiscal.manipulacao_dados import (
    GEMINI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    extrair_com_gemini,
    extrair_com_claude,
    extrair_com_openai,
)

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
