import { useState } from 'react'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function ConsultaRAG() {
  const [pergunta, setPergunta] = useState('')
  const [modo, setModo] = useState('simples')
  const [carregando, setCarregando] = useState(false)
  const [resposta, setResposta] = useState(null)
  const [erro, setErro] = useState(null)

  async function consultar() {
    if (!pergunta.trim()) {
      alert('Digite uma pergunta.')
      return
    }
    setCarregando(true)
    setErro(null)
    setResposta(null)
    try {
      const res = await fetch(`${API}/consultar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta, modo }),
      })
      const json = await res.json()
      if (!res.ok) {
        setErro(json.erro ?? `Erro ${res.status}`)
        return
      }
      if (json.erro) {
        setErro(json.erro)
        return
      }
      setResposta(json.resposta)
    } catch {
      setErro('Erro ao conectar com o servidor.')
    } finally {
      setCarregando(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      consultar()
    }
  }

  return (
    <main className="upload-container">
      <div className="upload-header">
        <h1 className="upload-title">Consulta Inteligente</h1>
        <p className="upload-subtitle">Faça perguntas sobre os dados financeiros usando IA</p>
      </div>

      <div className="upload-card">
        <div className="abas">
          <button
            className={modo === 'simples' ? 'aba ativo' : 'aba'}
            onClick={() => setModo('simples')}
          >
            RAG Simples
          </button>
          <button
            className={modo === 'embeddings' ? 'aba ativo' : 'aba'}
            onClick={() => setModo('embeddings')}
          >
            RAG Embeddings
          </button>
        </div>

        <p className="observacao">
          {modo === 'simples'
            ? 'Envia todos os registros do banco como contexto para a IA responder.'
            : 'Busca os registros mais relevantes por similaridade semântica antes de responder.'}
        </p>

        <label className="label">Sua pergunta</label>
        <textarea
          className="input-consulta"
          rows={3}
          value={pergunta}
          onChange={e => setPergunta(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ex: Qual o total gasto com insumos agrícolas? (Ctrl+Enter para enviar)"
        />

        <button
          className="upload-button"
          onClick={consultar}
          disabled={carregando}
        >
          {carregando ? 'Consultando...' : 'Consultar'}
        </button>
      </div>

      {erro && (
        <div className="upload-card" style={{ borderLeft: '4px solid #ef4444' }}>
          <p style={{ color: '#ef4444', margin: 0 }}>Erro: {erro}</p>
        </div>
      )}

      {resposta && (
        <div className="upload-card">
          <h2 className="resultado-titulo">Resposta da IA</h2>
          <p className="modo-badge">Modo: {modo === 'simples' ? 'RAG Simples' : 'RAG Embeddings'}</p>
          <p className="consulta-resposta">{resposta}</p>
        </div>
      )}
    </main>
  )
}
