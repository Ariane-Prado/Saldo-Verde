export default function TabelaCrud({ colunas, registros, onEditar, onExcluir, ordenacao, onOrdenar }) {
  function seta(campo) {
    if (ordenacao.campo !== campo) return ' ↕'
    return ordenacao.direcao === 'asc' ? ' ↑' : ' ↓'
  }

  return (
    <div className="crud-tabela-wrapper">
      <table className="crud-tabela">
        <thead>
          <tr>
            {colunas.map(col => (
              <th
                key={col.chave}
                className={`${col.ordenavel ? 'ordenavel' : ''} ${ordenacao.campo === col.chave ? 'ativo-ord' : ''}`}
                onClick={col.ordenavel ? () => onOrdenar(col.chave) : undefined}
              >
                {col.rotulo}
                {col.ordenavel && <span className="seta-ordem">{seta(col.chave)}</span>}
              </th>
            ))}
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {registros.length === 0 ? (
            <tr>
              <td colSpan={colunas.length + 1} className="crud-vazio">
                Nenhum registro encontrado.
              </td>
            </tr>
          ) : (
            registros.map((row, i) => (
              <tr key={row.id ?? i}>
                {colunas.map(col => (
                  <td key={col.chave}>
                    {col.render ? col.render(row[col.chave], row) : (row[col.chave] ?? '—')}
                  </td>
                ))}
                <td>
                  <div className="acoes-celula">
                    <button className="botao-editar" onClick={() => onEditar(row)}>Editar</button>
                    <button className="botao-excluir" onClick={() => onExcluir(row)}>Excluir</button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
