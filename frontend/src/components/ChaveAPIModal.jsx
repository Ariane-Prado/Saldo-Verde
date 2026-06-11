import { useState } from 'react'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function ChaveAPIModal({ onConfirmar }) {
  const [chave, setChave] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)

  async function confirmar(e) {
    if (e) e.preventDefault()
    if (!chave.trim()) {
      setErro('Informe a chave antes de continuar.')
      return
    }
    setCarregando(true)
    setErro(null)
    try {
      const res = await fetch(`${API}/configurar-chave`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gemini_key: chave }),
      })
      const json = await res.json()
      if (!res.ok || json.erro) {
        setErro(json.erro ?? `Erro ${res.status}`)
        return
      }
      onConfirmar()
    } catch {
      setErro('Não foi possível conectar ao servidor.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h2>Bem-vindo ao Saldo Verde</h2>
        <p>Para usar o sistema, informe sua chave da API Google Gemini.</p>

        <form onSubmit={confirmar} style={{ display: 'contents' }}>
          <label className="label" style={{ marginBottom: 4 }}>Chave da API Gemini</label>
          <input
            className="modal-input"
            type="password"
            value={chave}
            onChange={e => setChave(e.target.value)}
            placeholder="AIzaSy..."
            autoFocus
            autoComplete="current-password"
          />

          <a
            href="https://aistudio.google.com/apikey"
            target="_blank"
            rel="noreferrer"
          >
            Não tem uma chave? Obtenha gratuitamente aqui.
          </a>

          {erro && <p className="modal-erro">{erro}</p>}

          <button
            type="submit"
            className="botao"
            disabled={carregando}
            style={{ marginTop: 4 }}
          >
            {carregando ? 'Configurando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
