import { useState, useEffect } from 'react'
import TabelaCrud from './TabelaCrud'
import FormModal from './FormModal'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function fmtValor(v) {
  if (v == null) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const COLUNAS = [
  { chave: 'id',                      rotulo: 'ID',            ordenavel: true },
  { chave: 'tipo',                     rotulo: 'Tipo',          ordenavel: true,
    render: (v) => <span className={`badge badge--${v?.toLowerCase()}`}>{v}</span> },
  { chave: 'fornecedor_nome',          rotulo: 'Fornecedor',    ordenavel: true },
  { chave: 'faturado_nome',            rotulo: 'Faturado',      ordenavel: true },
  { chave: 'classificacao_descricao',  rotulo: 'Classificação', ordenavel: true },
  { chave: 'valor_total',              rotulo: 'Valor Total',   ordenavel: true, render: fmtValor },
  { chave: 'data_emissao',             rotulo: 'Data Emissão',  ordenavel: true },
]

export default function ManterContas() {
  const [registros, setRegistros]     = useState([])
  const [pessoas, setPessoas]         = useState([])
  const [classifs, setClassifs]       = useState([])
  const [carregando, setCarregando]   = useState(false)
  const [salvando, setSalvando]       = useState(false)
  const [erro, setErro]               = useState(null)
  const [erroModal, setErroModal]     = useState(null)
  const [modalAberto, setModalAberto] = useState(false)
  const [editando, setEditando]       = useState(null)
  const [ordenacao, setOrdenacao]     = useState({ campo: null, direcao: 'asc' })
  const [busca, setBusca]             = useState('')
  const [filtrTipo, setFiltrTipo]     = useState('')
  const [parcelas, setParcelas]       = useState([{ identificacao: '', data_vencimento: '', valor: '' }])

  useEffect(() => {
    fetch(`${API}/pessoas`).then(r => r.json()).then(j => setPessoas(j.registros ?? []))
    fetch(`${API}/classificacoes`).then(r => r.json()).then(j => setClassifs(j.registros ?? []))
  }, [])

  async function carregar(params = {}) {
    setCarregando(true); setErro(null)
    try {
      const qs = new URLSearchParams()
      if (params.q)    qs.set('q', params.q)
      if (params.tipo) qs.set('tipo', params.tipo)
      const res  = await fetch(`${API}/movimentos?${qs}`)
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
      if (typeof va === 'number') return direcao === 'asc' ? va - vb : vb - va
      return direcao === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va))
    }))
  }

  function abrirCriar() {
    setEditando(null)
    setParcelas([{ identificacao: '', data_vencimento: '', valor: '' }])
    setErroModal(null)
    setModalAberto(true)
  }

  async function abrirEditar(row) {
    setErroModal(null)
    try {
      const res  = await fetch(`${API}/movimentos/${row.id}`)
      const json = await res.json()
      setEditando(json)
      setParcelas(json.parcelas?.length ? json.parcelas : [{ identificacao: '', data_vencimento: '', valor: '' }])
    } catch {
      setEditando(row)
      setParcelas([{ identificacao: '', data_vencimento: '', valor: '' }])
    }
    setModalAberto(true)
  }

  function fecharModal() { setModalAberto(false); setEditando(null) }

  function addParcela() {
    setParcelas(prev => [...prev, { identificacao: '', data_vencimento: '', valor: '' }])
  }

  function removerParcela(i) {
    setParcelas(prev => prev.filter((_, idx) => idx !== i))
  }

  function atualizarParcela(i, campo, valor) {
    setParcelas(prev => prev.map((p, idx) => idx === i ? { ...p, [campo]: valor } : p))
  }

  async function salvar(dados) {
    setSalvando(true); setErroModal(null)
    const payload = {
      tipo:             dados.tipo,
      id_fornecedor:    dados.id_fornecedor ? Number(dados.id_fornecedor) : null,
      id_faturado:      dados.id_faturado   ? Number(dados.id_faturado)   : null,
      id_classificacao: dados.id_classificacao ? Number(dados.id_classificacao) : null,
      valor_total:      dados.valor_total ? Number(dados.valor_total) : null,
      data_emissao:     dados.data_emissao || null,
      parcelas:         parcelas.filter(p => p.valor).map((p, i) => ({
        identificacao:   p.identificacao || undefined,
        data_vencimento: p.data_vencimento || undefined,
        valor:           Number(p.valor),
      })),
    }
    try {
      const url    = editando ? `${API}/movimentos/${editando.id}` : `${API}/movimentos`
      const method = editando ? 'PUT' : 'POST'
      const res    = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
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
    if (!window.confirm(`Excluir movimento #${row.id}?`)) return
    const res  = await fetch(`${API}/movimentos/${row.id}`, { method: 'DELETE' })
    const json = await res.json()
    if (!res.ok) { setErro(json.erro ?? 'Erro ao excluir'); return }
    carregar({ q: busca, tipo: filtrTipo })
  }

  const fornecedores = pessoas.filter(p => p.tipo === 'FORNECEDOR')
  const faturados    = pessoas.filter(p => p.tipo === 'FATURADO')

  return (
    <div className="crud-pagina">
      <div className="crud-cabecalho">
        <h1 className="crud-titulo">Manter Contas</h1>
      </div>

      <div className="crud-toolbar">
        <input
          className="crud-input-busca"
          placeholder="Buscar por fornecedor, faturado, classificação..."
          value={busca}
          onChange={e => setBusca(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && carregar({ q: busca, tipo: filtrTipo })}
        />
        <select className="crud-select" value={filtrTipo} onChange={e => setFiltrTipo(e.target.value)}>
          <option value="">Todos os tipos</option>
          <option value="APAGAR">APAGAR</option>
          <option value="ARECEBER">ARECEBER</option>
        </select>
        <button className="botao-buscar" onClick={() => carregar({ q: busca, tipo: filtrTipo })} disabled={carregando}>
          {carregando ? 'Buscando...' : 'Buscar'}
        </button>
        <button className="botao-todos" onClick={() => { setBusca(''); setFiltrTipo(''); carregar({}) }} disabled={carregando}>
          Todos
        </button>
        <button className="botao-novo" onClick={abrirCriar}>+ Nova Conta</button>
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
        titulo={editando ? `Editar Conta #${editando.id}` : 'Nova Conta'}
        aberto={modalAberto}
        onFechar={fecharModal}
        onSubmit={salvar}
        carregando={salvando}
        erro={erroModal}
      >
        <div className="form-grupo">
          <label className="form-label">Tipo</label>
          <select name="tipo" className="form-select" defaultValue={editando?.tipo ?? 'APAGAR'} required>
            <option value="APAGAR">APAGAR</option>
            <option value="ARECEBER">ARECEBER</option>
          </select>
        </div>

        <div className="form-grupo">
          <label className="form-label">Fornecedor</label>
          <select name="id_fornecedor" className="form-select" defaultValue={editando?.id_fornecedor ?? ''}>
            <option value="">— Selecione —</option>
            {fornecedores.map(p => <option key={p.id} value={p.id}>{p.razao_social}</option>)}
          </select>
        </div>

        <div className="form-grupo">
          <label className="form-label">Faturado</label>
          <select name="id_faturado" className="form-select" defaultValue={editando?.id_faturado ?? ''}>
            <option value="">— Selecione —</option>
            {faturados.map(p => <option key={p.id} value={p.id}>{p.razao_social}</option>)}
          </select>
        </div>

        <div className="form-grupo">
          <label className="form-label">Classificação</label>
          <select name="id_classificacao" className="form-select" defaultValue={editando?.id_classificacao ?? ''}>
            <option value="">— Selecione —</option>
            {classifs.map(c => <option key={c.id} value={c.id}>{c.tipo} — {c.descricao}</option>)}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div className="form-grupo">
            <label className="form-label">Valor Total (R$)</label>
            <input name="valor_total" type="number" step="0.01" min="0" className="form-input"
              defaultValue={editando?.valor_total ?? ''} required />
          </div>
          <div className="form-grupo">
            <label className="form-label">Data de Emissão</label>
            <input name="data_emissao" type="date" className="form-input"
              defaultValue={editando?.data_emissao ?? ''} />
          </div>
        </div>

        <div className="parcelas-secao">
          <p className="parcelas-titulo">Parcelas</p>
          {parcelas.map((p, i) => (
            <div key={i} className="parcela-linha">
              <div className="form-grupo" style={{ gridColumn: '1/-1' }}>
                <label className="form-label">Identificação</label>
                <input className="form-input" value={p.identificacao}
                  onChange={e => atualizarParcela(i, 'identificacao', e.target.value)}
                  placeholder={`Parcela ${i + 1}`} />
              </div>
              <div className="form-grupo">
                <label className="form-label">Vencimento</label>
                <input type="date" className="form-input" value={p.data_vencimento}
                  onChange={e => atualizarParcela(i, 'data_vencimento', e.target.value)} />
              </div>
              <div className="form-grupo">
                <label className="form-label">Valor (R$)</label>
                <input type="number" step="0.01" min="0" className="form-input" value={p.valor}
                  onChange={e => atualizarParcela(i, 'valor', e.target.value)} />
              </div>
              {parcelas.length > 1 && (
                <button type="button" className="botao-remover-parcela" onClick={() => removerParcela(i)}
                  style={{ alignSelf: 'flex-end' }}>✕</button>
              )}
            </div>
          ))}
          <button type="button" className="botao-add-parcela" onClick={addParcela}>+ Adicionar Parcela</button>
        </div>
      </FormModal>
    </div>
  )
}
