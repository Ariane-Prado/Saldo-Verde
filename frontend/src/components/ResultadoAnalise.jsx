import "../App.css";

export default function ResultadoAnalise({ analise, dados }) {
  if (!analise) return null;

  const fornecedor = dados?.fornecedor ?? {};
  const faturado = dados?.faturado ?? {};
  const despesa = dados?.classificacao_despesa?.[0] ?? {};
  const descricaoDespesa =
    despesa.categoria && despesa.subcategoria
      ? despesa.categoria + " - " + despesa.subcategoria
      : despesa.categoria ?? dados?.descricao_produtos ?? "-";

  const entidades = [
    {
      titulo: "FORNECEDOR",
      nome: fornecedor.razao_social ?? fornecedor.fantasia ?? "-",
      documento: fornecedor.cnpj ?? "-",
      docLabel: "CNPJ",
      resultado: analise.fornecedor,
    },
    {
      titulo: "FATURADO",
      nome: faturado.nome_completo ?? faturado.razao_social ?? "-",
      documento: faturado.cpf ?? "-",
      docLabel: "CPF",
      resultado: analise.faturado,
    },
    {
      titulo: "DESPESA",
      nome: descricaoDespesa,
      documento: null,
      docLabel: null,
      resultado: analise.despesa,
    },
  ];

  function existe(res) {
    return res?.existe === true;
  }

  function idExibido(res) {
    return res?.id ?? res?.id_criado ?? "-";
  }

  return (
    <div className="analise-container">
      <h2 className="analise-header">Análise do Banco de Dados</h2>

      <div className="analise-entidades">
        {entidades.map(function (ent) {
          return (
            <div key={ent.titulo} className="analise-card">
              <h3 className="analise-card-titulo">{ent.titulo}</h3>
              <p className="analise-card-nome">{ent.nome}</p>

              {ent.documento && (
                <p className="analise-card-doc">
                  {ent.docLabel}: {ent.documento}
                </p>
              )}

              <div
                className={
                  "analise-status " +
                  (existe(ent.resultado)
                    ? "analise-status--existe"
                    : "analise-status--nao-existe")
                }
              >
                {existe(ent.resultado)
                  ? "EXISTE - ID: " + idExibido(ent.resultado)
                  : "NÃO EXISTE - CRIADO ID: " + idExibido(ent.resultado)}
              </div>
            </div>
          );
        })}
      </div>

      {analise.sucesso && (
        <div className="analise-sucesso">
          <span className="analise-sucesso-icone">&#x2705;</span>
          <div>
            <p className="analise-sucesso-titulo">
              Registro lançado com sucesso!
            </p>
            <p className="analise-sucesso-detalhe">
              Movimento <strong>#{analise.movimento_id}</strong> criado
              {analise.parcela_id != null && (
                <span>
                  {" "}
                  &middot; Parcela <strong>#{analise.parcela_id}</strong>
                </span>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
