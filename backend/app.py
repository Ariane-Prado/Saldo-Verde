from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

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

    return jsonify({
        "mensagem": "Arquivo recebido",
        "arquivo": filename
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)