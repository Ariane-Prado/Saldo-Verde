import { useState } from 'react'
import './App.css'
import UploadNota from './components/UploadNota'
import ConsultaRAG from './components/ConsultaRAG'

function App() {
  const [pagina, setPagina] = useState('upload')

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
