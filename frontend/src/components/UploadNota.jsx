import { useState } from "react";
import "../App.css";

const API = "http://localhost:8000";

const ORDEM_CAMPOS = [
  "fornecedor",
  "faturado",
  "numero_nota_fiscal",
  "data_emissao",
  "descricao_produtos",
  "parcelas",
  "valor_total",
  "classificacao_despesa",
];

function ordenarJSON(dados) {
  const ordenado = {};
  for (const campo of ORDEM_CAMPOS) {
    if (campo in dados) ordenado[campo] = dados[campo];
  }
  for (const campo of Object.keys(dados)) {
    if (!(campo in ordenado)) ordenado[campo] = dados[campo];
  }
  return ordenado;
}

export default function UploadNota() {
  const [arquivo, setArquivo] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);
  const [copiado, setCopiado] = useState(false);

  function selecionarArquivo(e) {
    setArquivo(e.target.files[0] || null);
    setResultado(null);
    setErro(null);
  }

  async function extrairDados() {
    if (!arquivo) {
      alert("Selecione um PDF primeiro.");
      return;
    }

    setCarregando(true);
    setErro(null);
    setResultado(null);

    const formData = new FormData();
    formData.append("file", arquivo);

    try {
      const resposta = await fetch(`${API}/extrair`, {
        method: "POST",
        body: formData,
      });
      const json = await resposta.json();

      if (json.erro) {
        setErro(json.erro);
      } else {
        setResultado(json.dados);
      }
    } catch {
      setErro("Erro ao conectar com o servidor. Verifique se o backend está rodando na porta 8000.");
    } finally {
      setCarregando(false);
    }
  }

  async function copiarJSON() {
    await navigator.clipboard.writeText(JSON.stringify(resultado, null, 2));
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
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

        {arquivo && (
          <div className="arquivo-info">
            <span>📄 {arquivo.name}</span>
            <span className="arquivo-tamanho">
              {(arquivo.size / (1024 * 1024)).toFixed(2)} MB
            </span>
          </div>
        )}

        <button className="botao" onClick={extrairDados} disabled={carregando}>
          {carregando ? "⏳ Processando..." : "⟳ EXTRAIR DADOS"}
        </button>
      </section>

      {erro && (
        <section className="card card--erro">
          <p>❌ {erro}</p>
        </section>
      )}

      {resultado && (
        <section className="card">
          <div className="json-topo">
            <span className="json-label">&lt;/&gt; Dados em JSON</span>
            <button className="botao-copiar" onClick={copiarJSON}>
              {copiado ? "✓ Copiado!" : "📋 Copiar JSON"}
            </button>
          </div>
          <div className="json-box">
            <pre>{JSON.stringify(ordenarJSON(resultado), null, 2)}</pre>
          </div>
          <p className="observacao">
            * Dados extraídos automaticamente pelo Gemini. Verifique antes de utilizar.
          </p>
        </section>
      )}
    </main>
  );
}
