import { useState } from 'react'
import './App.css'
import Login from './components/Login'
import Tutorial from './components/Tutorial'
import UploadNota from './components/UploadNota'
import ConsultaRAG from './components/ConsultaRAG'
import ChaveAPIModal from './components/ChaveAPIModal'
import ManterPessoas from './components/crud/ManterPessoas'
import ManterClassificacao from './components/crud/ManterClassificacao'
import ManterContas from './components/crud/ManterContas'

const PAGINAS_IA = ['upload', 'consulta']

const ITENS_NAV = [
  { id: 'upload',        rotulo: 'Nota Fiscal',   secao: 'IA' },
  { id: 'consulta',      rotulo: 'Consulta IA',   secao: 'IA' },
  { id: 'pessoas',       rotulo: 'Pessoas',        secao: 'Cadastros' },
  { id: 'classificacao', rotulo: 'Classificação',  secao: 'Cadastros' },
  { id: 'contas',        rotulo: 'Contas',         secao: 'Cadastros' },
]

function IconeChave({ ativo }) {
  const cor = ativo ? '#16a34a' : '#6b7280'
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke={cor} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="7.5" cy="15.5" r="5.5" />
      <path d="M21 2l-9.6 9.6" />
      <path d="M15.5 7.5l3 3L22 7l-3-3" />
    </svg>
  )
}

function App() {
  const [usuarioLogado, setUsuarioLogado]   = useState(() => localStorage.getItem('sv_usuario'))
  const [chaveOk, setChaveOk]               = useState(false)
  const [pagina, setPagina]                 = useState('pessoas')
  const [modalChave, setModalChave]         = useState(false)
  const [paginaPendente, setPaginaPendente] = useState(null)
  const [tutorialAberto, setTutorialAberto] = useState(false)

  function handleLogin(nome) {
    localStorage.setItem('sv_usuario', nome)
    setUsuarioLogado(nome)
    setTutorialAberto(true)
  }

  if (!usuarioLogado) {
    return <Login onLogin={handleLogin} />
  }

  function navegar(id) {
    if (PAGINAS_IA.includes(id) && !chaveOk) {
      setPaginaPendente(id)
      setModalChave(true)
      return
    }
    setPagina(id)
  }

  function confirmarChave() {
    setChaveOk(true)
    setModalChave(false)
    if (paginaPendente) {
      setPagina(paginaPendente)
      setPaginaPendente(null)
    }
  }

  function fecharModalChave() {
    setModalChave(false)
    setPaginaPendente(null)
  }

  function sair() {
    localStorage.removeItem('sv_usuario')
    setUsuarioLogado(null)
    setChaveOk(false)
    setPagina('pessoas')
    setTutorialAberto(false)
  }

  const secoes = [...new Set(ITENS_NAV.map(i => i.secao))]

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">Saldo Verde</div>

        <div className="sidebar-usuario">
          <span className="sidebar-usuario-nome">{usuarioLogado}</span>
          <button className="sidebar-sair-btn" onClick={sair}>Sair</button>
        </div>

        <nav className="sidebar-nav" data-tutorial="sidebar">
          {secoes.map(secao => (
            <div key={secao}>
              <span className="sidebar-secao">{secao}</span>
              {ITENS_NAV.filter(i => i.secao === secao).map(item => (
                <button
                  key={item.id}
                  className={pagina === item.id ? 'nav-ativo' : ''}
                  onClick={() => navegar(item.id)}
                  data-tutorial={`nav-${item.id}`}
                >
                  {item.rotulo}
                </button>
              ))}
            </div>
          ))}

        </nav>

        <button
          className="sidebar-chave-btn"
          onClick={() => setModalChave(true)}
          title={chaveOk ? 'Chave configurada — clique para alterar' : 'Configurar chave API'}
          data-tutorial="chave-btn"
        >
          <IconeChave ativo={chaveOk} />
          <span style={{ color: chaveOk ? '#16a34a' : '#6b7280' }}>
            {chaveOk ? 'Chave ativa' : 'Sem chave'}
          </span>
        </button>
      </aside>

      <main className="conteudo-principal">
        {pagina === 'upload'        && <UploadNota />}
        {pagina === 'consulta'      && <ConsultaRAG />}
        {pagina === 'pessoas'       && <ManterPessoas />}
        {pagina === 'classificacao' && <ManterClassificacao />}
        {pagina === 'contas'        && <ManterContas />}
      </main>

      {tutorialAberto && (
        <Tutorial onFechar={() => setTutorialAberto(false)} />
      )}

      {modalChave && (
        <ChaveAPIModal onConfirmar={confirmarChave} onFechar={fecharModalChave} />
      )}
    </div>
  )
}

export default App
