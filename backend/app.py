from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from agents.nota_fiscal.consulta_dados import extrair_dados_nota_fiscal
import repository

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensagem": "Backend funcionando"})

@app.route("/extrair", methods=["POST"])
def extrair():
    if "file" not in request.files:
        return jsonify({"erro": "Arquivo não enviado"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"erro": "Nome inválido"}), 400

    filename = secure_filename(file.filename)
    caminho = os.path.join(UPLOAD_FOLDER, filename)
    file.save(caminho)

    # Chama o agente de IA para extrair os dados
    dados = extrair_dados_nota_fiscal(caminho)

    return jsonify({
        "mensagem": "Arquivo processado com sucesso",
        "arquivo": filename,
        "dados": dados
    })

@app.route("/analisar", methods=["POST"])
def analisar():
    body = request.get_json(force=True)

    fornecedor_input = body.get("fornecedor", {})
    faturado_input   = body.get("faturado", {})
    despesa_input    = body.get("despesa", {})
    valor_total      = body.get("valor_total", 0)
    data_emissao     = body.get("data_emissao")
    parcelas         = body.get("parcelas", [])

    # --- FORNECEDOR ---
    res_forn = repository.buscar_fornecedor(fornecedor_input.get("cnpj"))
    if res_forn["existe"]:
        id_fornecedor = res_forn["id"]
        forn_resp = {"existe": True, "id": id_fornecedor}
    else:
        id_fornecedor = repository.criar_fornecedor(fornecedor_input)
        forn_resp = {"existe": False, "id_criado": id_fornecedor}

    # --- FATURADO ---
    res_fat = repository.buscar_faturado(faturado_input.get("cpf"))
    if res_fat["existe"]:
        id_faturado = res_fat["id"]
        fat_resp = {"existe": True, "id": id_faturado}
    else:
        id_faturado = repository.criar_faturado(faturado_input)
        fat_resp = {"existe": False, "id_criado": id_faturado}

    # --- DESPESA ---
    descricao_despesa = despesa_input.get("descricao", "")
    res_desp = repository.buscar_despesa(descricao_despesa)
    if res_desp["existe"]:
        id_classificacao = res_desp["id"]
        desp_resp = {"existe": True, "id": id_classificacao}
    else:
        id_classificacao = repository.criar_despesa(descricao_despesa)
        desp_resp = {"existe": False, "id_criado": id_classificacao}

    # --- MOVIMENTO ---
    id_movimento = repository.criar_movimento({
        "id_fornecedor":   id_fornecedor,
        "id_faturado":     id_faturado,
        "id_classificacao": id_classificacao,
        "valor_total":     valor_total,
        "data_emissao":    data_emissao,
    })

    # --- PARCELAS ---
    ultimo_id_parcela = None
    if parcelas:
        for p in parcelas:
            identificacao = f"MOV{id_movimento}-PARC{p.get('numero', 1)}"
            ultimo_id_parcela = repository.criar_parcela(id_movimento, {
                "identificacao":   identificacao,
                "data_vencimento": p.get("data_vencimento"),
                "valor":           p.get("valor", valor_total),
            })
    else:
        ultimo_id_parcela = repository.criar_parcela(id_movimento, {
            "identificacao":   f"MOV{id_movimento}-PARC1",
            "data_vencimento": None,
            "valor":           valor_total,
        })

    return jsonify({
        "fornecedor":  forn_resp,
        "faturado":    fat_resp,
        "despesa":     desp_resp,
        "movimento_id": id_movimento,
        "parcela_id":   ultimo_id_parcela,
        "sucesso":     True,
    })


if __name__ == "__main__":
    app.run(debug=True, port=8000)