import { useState } from 'react'
import TabelaCrud from './TabelaCrud'
import FormModal from './FormModal'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const COLUNAS = [
  { chave: 'id',       rotulo: 'ID',       ordenavel: true },
  { chave: 'tipo',     rotulo: 'Tipo',     ordenavel: true, render: (v) => <span className={`badge badge--${v?.toLowerCase()}`}>{v}</span> },
  { chave: 'descricao',rotulo: 'Descrição',ordenavel: true },
]

export default function ManterClassificacao() {
  const [registros, setRegistros]         = useState([])
  const [carregando, setCarregando]       = useState(false)
  const [salvando, setSalvando]           = useState(false)
  const [erro, setErro]                   = useState(null)
  const [erroModal, setErroModal]         = useState(null)
  const [modalAberto, setModalAberto]     = useState(false)
  const [editando, setEditando]           = useState(null)
  const [ordenacao, setOrdenacao]         = useState({ campo: null, direcao: 'asc' })
  const [busca, setBusca]                 = useState('')
  const [filtrTipo, setFiltrTipo]         = useState('')

  async function carregar(params = {}) {
    setCarregando(true)
    setErro(null)
    try {
      const qs = new URLSearchParams()
      if (params.q)    qs.set('q', params.q)
      if (params.tipo) qs.set('tipo', params.tipo)
      const res = await fetch(`${API}/classificacoes?${qs}`)
      const json = await res.json()
      if (!res.ok) { setErro(json.erro ?? `Erro ${res.status}`); return }
      setRegistros(json.registros)
    } catch {
      setErro('Falha na conexão com o servidor.')
    } finally {
      setCarregando(false)
    }
  }

  function ordenar(campo) {
    const direcao = ordenacao.campo === campo && ordenacao.direcao === 'asc' ? 'desc' : 'asc'
    setOrdenacao({ campo, direcao })
    setRegistros(prev => [...prev].sort((a, b) => {
      const va = a[campo] ?? ''; const vb = b[campo] ?? ''
      return direcao === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va))
    }))
  }

  function abrirCriar() { setEditando(null); setErroModal(null); setModalAberto(true) }
  function abrirEditar(row) { setEditando(row); setErroModal(null); setModalAberto(true) }
  function fecharModal() { setModalAberto(false); setEditando(null) }

  async function salvar(dados) {
    setSalvando(true); setErroModal(null)
    try {
      const url    = editando ? `${API}/classificacoes/${editando.id}` : `${API}/classificacoes`
      const method = editando ? 'PUT' : 'POST'
      const res    = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) })
      const json   = await res.json()
      if (!res.ok) { setErroModal(json.erro ?? `Erro ${res.status}`); return }
      fecharModal()
      carregar({ q: busca, tipo: filtrTipo })
    } catch {
      setErroModal('Falha ao salvar.')
    } finally {
      setSalvando(false)
    }
  }

  async function excluir(row) {
    if (!window.confirm(`Excluir "${row.descricao}"?`)) return
    const res  = await fetch(`${API}/classificacoes/${row.id}`, { method: 'DELETE' })
    const json = await res.json()
    if (!res.ok) { setErro(json.erro ?? 'Erro ao excluir'); return }
    carregar({ q: busca, tipo: filtrTipo })
  }

  return (
    <div className="crud-pagina">
      <div className="crud-cabecalho">
        <h1 className="crud-titulo">Manter Classificação</h1>
      </div>

      <div className="crud-toolbar">
        <input
          className="crud-input-busca"
          placeholder="Buscar por descrição..."
          value={busca}
          onChange={e => setBusca(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && carregar({ q: busca, tipo: filtrTipo })}
        />
        <select className="crud-select" value={filtrTipo} onChange={e => setFiltrTipo(e.target.value)}>
          <option value="">Todos os tipos</option>
          <option value="DESPESA">DESPESA</option>
          <option value="RECEITA">RECEITA</option>
        </select>
        <button className="botao-buscar" onClick={() => carregar({ q: busca, tipo: filtrTipo })} disabled={carregando}>
          {carregando ? 'Buscando...' : 'Buscar'}
        </button>
        <button className="botao-todos" onClick={() => { setBusca(''); setFiltrTipo(''); carregar({}) }} disabled={carregando}>
          Todos
        </button>
        <button className="botao-novo" onClick={abrirCriar}>+ Nova Classificação</button>
      </div>

      {erro && <p className="card--erro">{erro}</p>}

      <TabelaCrud
        colunas={COLUNAS}
        registros={registros}
        onEditar={abrirEditar}
        onExcluir={excluir}
        ordenacao={ordenacao}
        onOrdenar={ordenar}
      />

      <FormModal
        titulo={editando ? 'Editar Classificação' : 'Nova Classificação'}
        aberto={modalAberto}
        onFechar={fecharModal}
        onSubmit={salvar}
        carregando={salvando}
        erro={erroModal}
      >
        <div className="form-grupo">
          <label className="form-label">Tipo</label>
          <select name="tipo" className="form-select" defaultValue={editando?.tipo ?? 'DESPESA'} required>
            <option value="DESPESA">DESPESA</option>
            <option value="RECEITA">RECEITA</option>
          </select>
        </div>
        <div className="form-grupo">
          <label className="form-label">Descrição</label>
          <input name="descricao" className="form-input" defaultValue={editando?.descricao ?? ''} required />
        </div>
      </FormModal>
    </div>
  )
}
