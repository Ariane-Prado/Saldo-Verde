import { useState } from "react";
import "../App.css";
import ResultadoAnalise from "./ResultadoAnalise";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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

function fmtValor(v) {
  if (v == null || v === "") return "—";
  const n = Number(v);
  if (Number.isNaN(n)) return String(v);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function ResumoEstruturado({ dados }) {
  const f = dados.fornecedor ?? {};
  const fat = dados.faturado ?? {};
  const parcelas = Array.isArray(dados.parcelas) ? dados.parcelas : [];
  const classif = Array.isArray(dados.classificacao_despesa)
    ? dados.classificacao_despesa
    : [];

  return (
    <div className="resumo-grid">
      <div className="resumo-bloco">
        <h3 className="resumo-titulo">Fornecedor</h3>
        <p>
          <span className="resumo-label">Razão social:</span>{" "}
          {f.razao_social ?? "—"}
        </p>
        <p>
          <span className="resumo-label">Fantasia:</span> {f.fantasia ?? "—"}
        </p>
        <p>
          <span className="resumo-label">CNPJ:</span> {f.cnpj ?? "—"}
        </p>
      </div>
      <div className="resumo-bloco">
        <h3 className="resumo-titulo">Faturado</h3>
        <p>
          <span className="resumo-label">Nome:</span>{" "}
          {fat.nome_completo ?? "—"}
        </p>
        <p>
          <span className="resumo-label">CPF:</span> {fat.cpf ?? "—"}
        </p>
      </div>
      <div className="resumo-bloco resumo-bloco--full">
        <h3 className="resumo-titulo">Nota</h3>
        <p>
          <span className="resumo-label">Nº NF:</span>{" "}
          {dados.numero_nota_fiscal ?? "—"}
        </p>
        <p>
          <span className="resumo-label">Data emissão:</span>{" "}
          {dados.data_emissao ?? "—"}
        </p>
        <p>
          <span className="resumo-label">Valor total:</span>{" "}
          {fmtValor(dados.valor_total)}
        </p>
        <p className="resumo-descricao">
          <span className="resumo-label">Produtos/serviços:</span>{" "}
          {dados.descricao_produtos ?? "—"}
        </p>
      </div>
      {parcelas.length > 0 && (
        <div className="resumo-bloco resumo-bloco--full">
          <h3 className="resumo-titulo">Parcelas</h3>
          <table className="resumo-tabela">
            <thead>
              <tr>
                <th>Nº</th>
                <th>Vencimento</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              {parcelas.map((p, i) => (
                <tr key={i}>
                  <td>{p?.numero ?? "—"}</td>
                  <td>{p?.data_vencimento ?? "—"}</td>
                  <td>{fmtValor(p?.valor)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {classif.length > 0 && (
        <div className="resumo-bloco resumo-bloco--full">
          <h3 className="resumo-titulo">Classificação de despesa</h3>
          <ul className="resumo-lista-classif">
            {classif.map((c, i) => (
              <li key={i} className="resumo-item-classif">
                <strong>{c?.categoria ?? "—"}</strong>
                {c?.subcategoria != null && (
                  <span className="resumo-sub"> · {c.subcategoria}</span>
                )}
                {c?.justificativa != null && (
                  <p className="resumo-justif">{c.justificativa}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function UploadNota() {
  const [arquivo, setArquivo] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);
  const [copiado, setCopiado] = useState(false);
  const [aba, setAba] = useState("resumo");
  const [analise, setAnalise] = useState(null);
  const [analisando, setAnalisando] = useState(false);

  function selecionarArquivo(e) {
    setArquivo(e.target.files[0] || null);
    setResultado(null);
    setErro(null);
    setAnalise(null);
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

      if (!resposta.ok) {
        setErro(json.erro ?? `Erro HTTP ${resposta.status}`);
        return;
      }

      if (json.erro) {
        setErro(json.erro);
        return;
      }

      const dados = json.dados;
      if (dados && typeof dados === "object" && dados.erro) {
        setErro(String(dados.erro));
        return;
      }

      setResultado(dados);
      setAba("resumo");

      // --- 2ª ETAPA: chamar POST /analisar ---
      await analisarDados(dados);
    } catch {
      setErro(
        "Erro ao conectar com o servidor. Verifique se o backend está rodando na porta 8000."
      );
    } finally {
      setCarregando(false);
    }
  }

  async function analisarDados(dados) {
    setAnalisando(true);
    setAnalise(null);
    try {
      const f = dados.fornecedor ?? {};
      const fat = dados.faturado ?? {};
      const classif = Array.isArray(dados.classificacao_despesa)
        ? dados.classificacao_despesa[0]
        : {};
      const parcelas = Array.isArray(dados.parcelas) ? dados.parcelas : [];

      const body = {
        fornecedor: {
          razao_social: f.razao_social ?? f.fantasia ?? "",
          cnpj: f.cnpj ?? "",
        },
        faturado: {
          razao_social: fat.nome_completo ?? fat.razao_social ?? "",
          cpf: fat.cpf ?? "",
        },
        despesa: {
          descricao: classif?.categoria
            ? `${classif.categoria}${classif.subcategoria ? " — " + classif.subcategoria : ""}`
            : dados.descricao_produtos ?? "",
        },
        valor_total: Number(dados.valor_total) || 0,
        data_emissao: dados.data_emissao ?? null,
        parcelas: parcelas.map((p) => ({
          numero: p.numero ?? 1,
          data_vencimento: p.data_vencimento ?? null,
          valor: Number(p.valor) || 0,
        })),
      };

      const resp = await fetch(`${API}/analisar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const respostaAnalise = await resp.json();

      if (!resp.ok) {
        setErro(respostaAnalise.erro ?? `Erro na análise: HTTP ${resp.status}`);
        return;
      }

      setAnalise(respostaAnalise);
    } catch {
      setErro("Erro ao conectar com /analisar. Verifique se o banco de dados está rodando.");
    } finally {
      setAnalisando(false);
    }
  }

  async function copiarJSON() {
    await navigator.clipboard.writeText(
      JSON.stringify(ordenarJSON(resultado), null, 2)
    );
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  }

  return (
    <main className="pagina">
      <section className="cabecalho">
        <h1>Extração de Dados de Nota Fiscal</h1>
        <p>
          Carregue um PDF de nota fiscal e extraia os dados automaticamente
          usando IA
        </p>
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
        <section className="card resultado">
          <h2 className="resultado-titulo">Resultado da extração</h2>
          <div className="abas" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={aba === "resumo"}
              className={aba === "resumo" ? "ativo" : ""}
              onClick={() => setAba("resumo")}
            >
              Resumo
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={aba === "json"}
              className={aba === "json" ? "ativo" : ""}
              onClick={() => setAba("json")}
            >
              JSON
            </button>
          </div>

          {aba === "resumo" && <ResumoEstruturado dados={resultado} />}

          {aba === "json" && (
            <>
              <div className="json-topo">
                <span className="json-label">&lt;/&gt; Dados em JSON</span>
                <button type="button" className="botao-copiar" onClick={copiarJSON}>
                  {copiado ? "✓ Copiado!" : "📋 Copiar JSON"}
                </button>
              </div>
              <div className="json-box">
                <pre>{JSON.stringify(ordenarJSON(resultado), null, 2)}</pre>
              </div>
            </>
          )}

          <p className="observacao">
            * Dados extraídos automaticamente por IA. Verifique antes de
            utilizar.
          </p>
        </section>
      )}

      {analisando && (
        <section className="card analise-loading">
          <p>⏳ Analisando dados no banco de dados...</p>
        </section>
      )}

      {analise && <ResultadoAnalise analise={analise} dados={resultado} />}
    </main>
  );
}
