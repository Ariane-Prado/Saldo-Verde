import { useState } from 'react'
import './App.css'
import UploadNota from './components/UploadNota'
import ConsultaRAG from './components/ConsultaRAG'
import ChaveAPIModal from './components/ChaveAPIModal'
import ManterPessoas from './components/crud/ManterPessoas'
import ManterClassificacao from './components/crud/ManterClassificacao'
import ManterContas from './components/crud/ManterContas'

const ITENS_NAV = [
  { id: 'upload',        rotulo: 'Nota Fiscal',          secao: 'IA' },
  { id: 'consulta',      rotulo: 'Consulta IA',           secao: 'IA' },
  { id: 'pessoas',       rotulo: 'Manter Pessoas',        secao: 'Cadastros' },
  { id: 'classificacao', rotulo: 'Manter Classificação',  secao: 'Cadastros' },
  { id: 'contas',        rotulo: 'Manter Contas',         secao: 'Cadastros' },
]

function App() {
  const [chaveOk, setChaveOk] = useState(false)
  const [pagina, setPagina]   = useState('upload')

  if (!chaveOk) {
    return <ChaveAPIModal onConfirmar={() => setChaveOk(true)} />
  }

  const secoes = [...new Set(ITENS_NAV.map(i => i.secao))]

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">Saldo Verde</div>
        <nav className="sidebar-nav">
          {secoes.map(secao => (
            <div key={secao}>
              <span className="sidebar-secao">{secao}</span>
              {ITENS_NAV.filter(i => i.secao === secao).map(item => (
                <button
                  key={item.id}
                  className={pagina === item.id ? 'nav-ativo' : ''}
                  onClick={() => setPagina(item.id)}
                >
                  {item.rotulo}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      <main className="conteudo-principal">
        {pagina === 'upload'        && <UploadNota />}
        {pagina === 'consulta'      && <ConsultaRAG />}
        {pagina === 'pessoas'       && <ManterPessoas />}
        {pagina === 'classificacao' && <ManterClassificacao />}
        {pagina === 'contas'        && <ManterContas />}
      </main>
    </div>
  )
}

export default App
