import { useState } from 'react'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Login({ onLogin }) {
  const [email, setEmail]         = useState('')
  const [senha, setSenha]         = useState('')
  const [erro, setErro]           = useState(null)
  const [carregando, setCarregando] = useState(false)

  async function entrar(e) {
    e.preventDefault()
    setErro(null)
    setCarregando(true)
    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      })
      const json = await res.json()
      if (!res.ok) {
        setErro(json.erro ?? 'Erro ao autenticar.')
      } else {
        onLogin(json.nome)
      }
    } catch {
      setErro('Não foi possível conectar ao servidor.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="login-pagina">
      <div className="login-card">

        <div className="login-marca">
          <div className="login-icone">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
              stroke="#16a34a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <h1 className="login-titulo">Saldo Verde</h1>
          <p className="login-subtitulo">Sistema Administrativo-Financeiro</p>
        </div>

        <form className="login-form" onSubmit={entrar}>
          <div className="login-grupo">
            <label className="login-label">E-mail</label>
            <input
              className="login-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Digite seu e-mail"
              autoFocus
              autoComplete="email"
            />
          </div>

          <div className="login-grupo">
            <label className="login-label">Senha</label>
            <input
              className="login-input"
              type="password"
              value={senha}
              onChange={e => setSenha(e.target.value)}
              placeholder="Digite sua senha"
              autoComplete="current-password"
            />
          </div>

          {erro && <p className="login-erro">{erro}</p>}

          <button className="login-btn" type="submit" disabled={carregando}>
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <p className="login-rodape">Universidade de Rio Verde — Projeto N3</p>
      </div>
    </div>
  )
}
