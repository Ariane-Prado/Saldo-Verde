_runtime = {}


def set_gemini_key(chave):
    _runtime["GEMINI_API_KEY"] = chave


def get_gemini_key():
    return _runtime.get("GEMINI_API_KEY")
