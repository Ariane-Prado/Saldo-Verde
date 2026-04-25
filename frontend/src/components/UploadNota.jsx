import "../App.css";

export default function UploadNota() {
  return (
    <main className="pagina">
      {/* Cabeçalho */}
      <section className="cabecalho">
        <h1>Extração de Dados de Nota Fiscal</h1>
        <p>
          Carregue um PDF de nota fiscal e extraia os dados automaticamente usando IA
        </p>
      </section>

      {/* Card Upload */}
      <section className="card">
        <div className="card-titulo">
          <span>⬆</span>
          <h2>Upload do PDF</h2>
        </div>

        <label className="label">
          Selecione o arquivo PDF da nota fiscal
        </label>

        <input
          className="input-arquivo"
          type="file"
          accept="application/pdf"
        />

        <button className="botao">
          ⟳ EXTRAIR DADOS
        </button>
      </section>

      {/* Card Resultado (vazio por enquanto) */}
      <section className="card resultado">
        <h2>Dados Extraídos</h2>

        <div className="abas">
          <button>Visualização Formatada</button>
          <button className="ativo">JSON</button>
        </div>

        <div className="json-topo">
          <h3>&lt;&gt; Dados em JSON</h3>
          <button disabled>📋 Copiar JSON</button>
        </div>

        <div className="json-box">
          <p style={{ color: "#9ca3af" }}>
            Nenhum dado carregado ainda...
          </p>
        </div>

        <p className="observacao">
          Os dados aparecerão aqui após a extração da nota fiscal.
        </p>
      </section>
    </main>
  );
}