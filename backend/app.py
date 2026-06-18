from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from agents.nota_fiscal.consulta_dados import extrair_dados_nota_fiscal
from agents.rag.consulta_rag import consultar_rag_simples, consultar_rag_embeddings, reset_vector_store
import agents.rag.consulta_rag as _rag_module
import agents.nota_fiscal.manipulacao_dados as _md_module
import config
import repository

app = Flask(__name__)
CORS(app)

from database import init_db
init_db()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"mensagem": "Backend funcionando"})


@app.route("/logout", methods=["POST"])
def logout():
    config.set_gemini_key(None)
    _rag_module.gemini_client = None
    _md_module.gemini_client = None
    return jsonify({"ok": True})


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

    fornecedor_input  = body.get("fornecedor", {})
    faturado_input    = body.get("faturado", {})
    despesa_input     = body.get("despesa", {})
    valor_total       = body.get("valor_total", 0)
    data_emissao      = body.get("data_emissao")
    parcelas          = body.get("parcelas", [])
    descricao_itens   = body.get("descricao_itens", "")

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
        "descricao_itens": descricao_itens,
    })

    # --- PARCELAS ---
    ultimo_id_parcela = None
    if parcelas:
        for p in parcelas:
            identificacao = f"MOV{id_movimento}-PARC{p.get('numero', 1)}"
            ultimo_id_parcela = repository.criar_parcela(id_movimento, {
                "identificacao":   identificacao,
                "data_vencimento": p.get("data_vencimento") or data_emissao,
                "valor":           p.get("valor", valor_total),
            })
    else:
        ultimo_id_parcela = repository.criar_parcela(id_movimento, {
            "identificacao":   f"MOV{id_movimento}-PARC1",
            "data_vencimento": data_emissao,
            "valor":           valor_total,
        })

    # Invalida o índice vetorial para que o novo movimento seja indexado na próxima consulta
    reset_vector_store()

    return jsonify({
        "fornecedor":  forn_resp,
        "faturado":    fat_resp,
        "despesa":     desp_resp,
        "movimento_id": id_movimento,
        "parcela_id":   ultimo_id_parcela,
        "sucesso":     True,
    })


@app.route("/status-chave", methods=["GET"])
def status_chave():
    chave = config.get_gemini_key() or os.getenv("GEMINI_API_KEY", "")
    return jsonify({"configurada": bool(chave)})


@app.route("/configurar-chave", methods=["POST"])
def configurar_chave():
    body = request.get_json(force=True)
    chave = body.get("gemini_key", "").strip()
    if not chave:
        return jsonify({"erro": "Chave não informada"}), 400
    config.set_gemini_key(chave)
    # Invalida clientes cacheados para forçar recriação com a nova chave
    _rag_module.gemini_client = None
    _md_module.gemini_client = None
    return jsonify({"ok": True})


@app.route("/consultar", methods=["POST"])
def consultar():
    body = request.get_json(force=True)
    pergunta = body.get("pergunta", "").strip()
    modo = body.get("modo", "simples")

    if not pergunta:
        return jsonify({"erro": "Pergunta não informada"}), 400

    try:
        if modo == "embeddings":
            resposta = consultar_rag_embeddings(pergunta)
        else:
            resposta = consultar_rag_simples(pergunta)
        return jsonify({"resposta": resposta, "modo": modo})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─────────────────────────────────────────────────────────────
# CRUD — Pessoas
# ─────────────────────────────────────────────────────────────

@app.route("/pessoas", methods=["GET"])
def rota_listar_pessoas():
    q    = request.args.get("q", "").strip() or None
    tipo = request.args.get("tipo", "").strip() or None
    return jsonify({"registros": repository.listar_pessoas(q=q, tipo=tipo)})


@app.route("/pessoas/<int:id>", methods=["GET"])
def rota_obter_pessoa(id):
    pessoa = repository.obter_pessoa(id)
    if pessoa is None:
        return jsonify({"erro": "Pessoa não encontrada"}), 404
    return jsonify(pessoa)


@app.route("/pessoas", methods=["POST"])
def rota_criar_pessoa():
    dados = request.get_json(force=True)
    if not dados.get("razao_social"):
        return jsonify({"erro": "razao_social é obrigatório"}), 400
    if dados.get("tipo") not in ("FORNECEDOR", "CLIENTE", "FATURADO"):
        return jsonify({"erro": "tipo deve ser FORNECEDOR, CLIENTE ou FATURADO"}), 400
    try:
        novo_id = repository.inserir_pessoa(dados)
        return jsonify({"id": novo_id}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/pessoas/<int:id>", methods=["PUT"])
def rota_atualizar_pessoa(id):
    dados = request.get_json(force=True)
    if not dados.get("razao_social"):
        return jsonify({"erro": "razao_social é obrigatório"}), 400
    try:
        ok = repository.atualizar_pessoa(id, dados)
        if not ok:
            return jsonify({"erro": "Pessoa não encontrada"}), 404
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/pessoas/<int:id>", methods=["DELETE"])
def rota_excluir_pessoa(id):
    ok = repository.desativar_pessoa(id)
    if not ok:
        return jsonify({"erro": "Pessoa não encontrada"}), 404
    return jsonify({"ok": True})


# ─────────────────────────────────────────────────────────────
# CRUD — Classificação
# ─────────────────────────────────────────────────────────────

@app.route("/classificacoes", methods=["GET"])
def rota_listar_classificacoes():
    q    = request.args.get("q", "").strip() or None
    tipo = request.args.get("tipo", "").strip() or None
    return jsonify({"registros": repository.listar_classificacoes(q=q, tipo=tipo)})


@app.route("/classificacoes/<int:id>", methods=["GET"])
def rota_obter_classificacao(id):
    cls = repository.obter_classificacao(id)
    if cls is None:
        return jsonify({"erro": "Classificação não encontrada"}), 404
    return jsonify(cls)


@app.route("/classificacoes", methods=["POST"])
def rota_criar_classificacao():
    dados = request.get_json(force=True)
    if not dados.get("descricao"):
        return jsonify({"erro": "descricao é obrigatória"}), 400
    if dados.get("tipo") not in ("DESPESA", "RECEITA"):
        return jsonify({"erro": "tipo deve ser DESPESA ou RECEITA"}), 400
    try:
        novo_id = repository.inserir_classificacao(dados)
        return jsonify({"id": novo_id}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/classificacoes/<int:id>", methods=["PUT"])
def rota_atualizar_classificacao(id):
    dados = request.get_json(force=True)
    if not dados.get("descricao"):
        return jsonify({"erro": "descricao é obrigatória"}), 400
    try:
        ok = repository.atualizar_classificacao(id, dados)
        if not ok:
            return jsonify({"erro": "Classificação não encontrada"}), 404
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/classificacoes/<int:id>", methods=["DELETE"])
def rota_excluir_classificacao(id):
    ok = repository.desativar_classificacao(id)
    if not ok:
        return jsonify({"erro": "Classificação não encontrada"}), 404
    return jsonify({"ok": True})


# ─────────────────────────────────────────────────────────────
# CRUD — MovimentoContas
# ─────────────────────────────────────────────────────────────

@app.route("/movimentos", methods=["GET"])
def rota_listar_movimentos():
    q    = request.args.get("q", "").strip() or None
    tipo = request.args.get("tipo", "").strip() or None
    return jsonify({"registros": repository.listar_movimentos(q=q, tipo=tipo)})


@app.route("/movimentos/<int:id>", methods=["GET"])
def rota_obter_movimento(id):
    mov = repository.obter_movimento_completo(id)
    if mov is None:
        return jsonify({"erro": "Movimento não encontrado"}), 404
    return jsonify(mov)


@app.route("/movimentos", methods=["POST"])
def rota_criar_movimento():
    dados = request.get_json(force=True)
    if dados.get("tipo") not in ("APAGAR", "ARECEBER"):
        return jsonify({"erro": "tipo deve ser APAGAR ou ARECEBER"}), 400
    if not dados.get("valor_total"):
        return jsonify({"erro": "valor_total é obrigatório"}), 400
    try:
        novo_id = repository.inserir_movimento_crud(dados)
        reset_vector_store()
        return jsonify({"id": novo_id}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/movimentos/<int:id>", methods=["PUT"])
def rota_atualizar_movimento(id):
    dados = request.get_json(force=True)
    try:
        ok = repository.atualizar_movimento_crud(id, dados)
        if not ok:
            return jsonify({"erro": "Movimento não encontrado"}), 404
        reset_vector_store()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/movimentos/<int:id>", methods=["DELETE"])
def rota_excluir_movimento(id):
    ok = repository.desativar_movimento(id)
    if not ok:
        return jsonify({"erro": "Movimento não encontrado"}), 404
    reset_vector_store()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
