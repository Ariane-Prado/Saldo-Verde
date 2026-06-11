import { useState } from 'react'
import './App.css'
import UploadNota from './components/UploadNota'
import ConsultaRAG from './components/ConsultaRAG'
import ChaveAPIModal from './components/ChaveAPIModal'

function App() {
  const [chaveOk, setChaveOk] = useState(false)
  const [pagina, setPagina] = useState('upload')

  if (!chaveOk) {
    return <ChaveAPIModal onConfirmar={() => setChaveOk(true)} />
  }

  return (
    <>
      <nav className="nav-principal">
        <button
          className={pagina === 'upload' ? 'nav-ativo' : ''}
          onClick={() => setPagina('upload')}
        >
          Nota Fiscal
        </button>
        <button
          className={pagina === 'consulta' ? 'nav-ativo' : ''}
          onClick={() => setPagina('consulta')}
        >
          Consulta IA
        </button>
      </nav>

      {pagina === 'upload' && <UploadNota />}
      {pagina === 'consulta' && <ConsultaRAG />}
    </>
  )
}

export default App
