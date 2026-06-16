import { useState } from 'react'
import './App.css'
import Login from './components/Login'
import Tutorial from './components/Tutorial'
import UploadNota from './components/UploadNota'
import ConsultaRAG from './components/ConsultaRAG'
import ManterPessoas from './components/crud/ManterPessoas'
import ManterClassificacao from './components/crud/ManterClassificacao'
import ManterContas from './components/crud/ManterContas'

const ITENS_NAV = [
  { id: 'upload',        rotulo: 'Nota Fiscal',   secao: 'IA' },
  { id: 'consulta',      rotulo: 'Consulta IA',   secao: 'IA' },
  { id: 'pessoas',       rotulo: 'Pessoas',        secao: 'Cadastros' },
  { id: 'classificacao', rotulo: 'Classificação',  secao: 'Cadastros' },
  { id: 'contas',        rotulo: 'Contas',         secao: 'Cadastros' },
]

function App() {
  const [usuarioLogado, setUsuarioLogado] = useState(() => localStorage.getItem('sv_usuario'))
  const [pagina, setPagina]               = useState('pessoas')
  const [tutorialAberto, setTutorialAberto] = useState(false)

  function handleLogin(nome) {
    localStorage.setItem('sv_usuario', nome)
    setUsuarioLogado(nome)
    setTutorialAberto(true)
  }

  if (!usuarioLogado) {
    return <Login onLogin={handleLogin} />
  }

  function sair() {
    localStorage.removeItem('sv_usuario')
    setUsuarioLogado(null)
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
                  onClick={() => setPagina(item.id)}
                  data-tutorial={`nav-${item.id}`}
                >
                  {item.rotulo}
                </button>
              ))}
            </div>
          ))}

          <span className="sidebar-secao">Ajuda</span>
          <button onClick={() => setTutorialAberto(true)} data-tutorial="nav-tutorial">
            Tutorial
          </button>
        </nav>
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
    </div>
  )
}

export default App
