export default function FormModal({ titulo, aberto, onFechar, onSubmit, carregando, erro, children }) {
  if (!aberto) return null

  function handleSubmit(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    const dados = Object.fromEntries(fd.entries())
    onSubmit(dados)
  }

  return (
    <div className="form-modal-overlay" onClick={onFechar}>
      <div className="form-modal-card" onClick={e => e.stopPropagation()}>
        <h2 className="form-modal-titulo">{titulo}</h2>
        <form onSubmit={handleSubmit}>
          {children}
          {erro && <p className="card--erro" style={{ margin: 0 }}>{erro}</p>}
          <div className="form-modal-rodape">
            <button type="button" className="botao-cancelar" onClick={onFechar} disabled={carregando}>
              Cancelar
            </button>
            <button type="submit" className="botao-salvar" disabled={carregando}>
              {carregando ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
