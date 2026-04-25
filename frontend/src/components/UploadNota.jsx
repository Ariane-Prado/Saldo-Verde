import { useState } from "react";
import "../App.css";

export default function UploadNota() {
  const [arquivo, setArquivo] = useState(null);

  function selecionarArquivo(event) {
    console.log("Arquivo selecionado:", event.target.files[0]);
    setArquivo(event.target.files[0]);
  }

  async function extrairDados() {
    console.log("Botão clicado");

    if (!arquivo) {
      console.log("Nenhum arquivo selecionado");
      alert("Selecione um PDF primeiro.");
      return;
    }

    const formData = new FormData();
    formData.append("file", arquivo);

    const resposta = await fetch("http://localhost:8000/extrair", {
      method: "POST",
      body: formData,
    });

    const dados = await resposta.json();
    console.log("Resposta do backend:", dados);
  }

  return (
    <main className="pagina">
      <section className="cabecalho">
        <h1>Extração de Dados de Nota Fiscal</h1>
        <p>Carregue um PDF de nota fiscal e extraia os dados automaticamente usando IA</p>
      </section>

      <section className="card">
        <div className="card-titulo">
          <span>⬆</span>
          <h2>Upload do PDF</h2>
        </div>

        <label className="label">Selecione o arquivo PDF da nota fiscal</label>

        <input
          className="input-arquivo"
          type="file"
          accept="application/pdf"
          onChange={selecionarArquivo}
        />

        <button className="botao" onClick={extrairDados}>
          ⟳ EXTRAIR DADOS
        </button>
      </section>
    </main>
  );
}