import { useState, useEffect } from 'react'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Dashboard({ navegar }) {
  const [resumo, setResumo] = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)

  async function carregarDados() {
    setCarregando(true)
    setErro(null)
    try {
      const res = await fetch(`${API}/dashboard/resumo`)
      if (!res.ok) {
        throw new Error(`Erro ${res.status}`)
      }
      const data = await res.json()
      setResumo(data)
    } catch (err) {
      setErro('Erro ao conectar com o servidor.')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    carregarDados()
  }, [])

  const formatarMoeda = (val) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(val ?? 0)
  }

  if (carregando) {
    return (
      <main className="pagina">
        <section className="cabecalho">
          <h1>Painel de Controle</h1>
          <p className="analise-loading">Carregando dados do painel...</p>
        </section>
      </main>
    )
  }

  if (erro) {
    return (
      <main className="pagina">
        <section className="cabecalho">
          <h1>Painel de Controle</h1>
        </section>
        <section className="card card--erro">
          <p>{erro}</p>
          <button className="botao-buscar" style={{ marginTop: '12px', width: 'auto' }} onClick={carregarDados}>
            Tentar novamente
          </button>
        </section>
      </main>
    )
  }

  const saldo = resumo?.saldo ?? 0
  const classeSaldo = saldo >= 0 ? 'saldo-positivo' : 'saldo-negativo'

  return (
    <main className="pagina">
      <section className="cabecalho">
        <h1>Painel de Controle</h1>
        <p>Resumo financeiro e ações rápidas do Saldo Verde</p>
      </section>

      {/* Grid de Métricas Principais */}
      <section className="dashboard-grid">
        <div className="dashboard-card card-receitas">
          <span className="dashboard-label">Total a Receber</span>
          <h2 className="dashboard-valor valor-receita">{formatarMoeda(resumo?.receitas)}</h2>
          <p className="dashboard-detalhe">Entradas ativas no sistema</p>
        </div>

        <div className="dashboard-card card-despesas">
          <span className="dashboard-label">Total a Pagar</span>
          <h2 className="dashboard-valor valor-despesa">{formatarMoeda(resumo?.despesas)}</h2>
          <p className="dashboard-detalhe">Saídas ativas no sistema</p>
        </div>

        <div className={`dashboard-card card-saldo ${classeSaldo}`}>
          <span className="dashboard-label">Saldo Líquido</span>
          <h2 className="dashboard-valor">{formatarMoeda(saldo)}</h2>
          <p className="dashboard-detalhe">Resultado (Receber - Pagar)</p>
        </div>
      </section>

      {/* Outras Métricas */}
      <section className="dashboard-subgrid" style={{ marginTop: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
        <div className="dashboard-card-mini">
          <span className="dashboard-mini-label">Contas Registradas</span>
          <h3>{resumo?.total_contas}</h3>
        </div>
        <div className="dashboard-card-mini">
          <span className="dashboard-mini-label">Pessoas Cadastradas</span>
          <h3>{resumo?.total_pessoas}</h3>
        </div>
        <div className="dashboard-card-mini">
          <span className="dashboard-mini-label">Categorias</span>
          <h3>{resumo?.total_classificacoes}</h3>
        </div>
      </section>

      {/* Ações Rápidas */}
      <section className="card" style={{ marginTop: '32px' }}>
        <h2 className="resultado-titulo">Ações Rápidas</h2>
        <p className="observacao" style={{ marginBottom: '20px' }}>Atalhos para as principais funcionalidades do sistema</p>
        
        <div className="dashboard-acoes-grid">
          <button className="botao-acao" onClick={() => navegar('contas')}>
            <div className="texto-acao">
              <strong>Registrar Conta</strong>
              <span>A pagar ou a receber</span>
            </div>
          </button>

          <button className="botao-acao" onClick={() => navegar('upload')}>
            <div className="texto-acao">
              <strong>Importar Nota Fiscal</strong>
              <span>Extração automática com IA</span>
            </div>
          </button>

          <button className="botao-acao" onClick={() => navegar('consulta')}>
            <div className="texto-acao">
              <strong>Consultar com IA</strong>
              <span>Pergunta em linguagem natural</span>
            </div>
          </button>

          <button className="botao-acao" onClick={() => navegar('pessoas')}>
            <div className="texto-acao">
              <strong>Nova Pessoa</strong>
              <span>Cliente, fornecedor ou faturado</span>
            </div>
          </button>
        </div>
      </section>
    </main>
  )
}
