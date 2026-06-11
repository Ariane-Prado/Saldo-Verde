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
    <main className="pagina">
      <section className="cabecalho">
        <h1>Consulta Inteligente</h1>
        <p>Faça perguntas sobre os dados financeiros usando IA</p>
      </section>

      <section className="card">
        <div className="abas">
          <button
            className={modo === 'simples' ? 'aba ativo' : 'aba'}
            onClick={() => { setModo('simples'); setResposta(null); setErro(null) }}
          >
            RAG Simples
          </button>
          <button
            className={modo === 'embeddings' ? 'aba ativo' : 'aba'}
            onClick={() => { setModo('embeddings'); setResposta(null); setErro(null) }}
          >
            RAG Embeddings
          </button>
        </div>

        <p className="observacao">
          {modo === 'simples'
            ? 'Envia os 20 registros mais recentes como contexto para a IA responder.'
            : 'Varre todos os registros e seleciona os 5 mais relevantes para a pergunta antes de responder.'}
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
          className="botao"
          onClick={consultar}
          disabled={carregando}
        >
          {carregando ? 'Consultando...' : 'Consultar'}
        </button>
      </section>

      {erro && (
        <section className="card card--erro">
          <p>Erro: {erro}</p>
        </section>
      )}

      {resposta && (
        <section className="card">
          <h2 className="resultado-titulo">Resposta da IA</h2>
          <p className="modo-badge">Modo: {modo === 'simples' ? 'RAG Simples' : 'RAG Embeddings'}</p>
          <p className="consulta-resposta">{resposta}</p>
        </section>
      )}
    </main>
  )
}
