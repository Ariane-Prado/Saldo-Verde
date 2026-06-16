import { useState } from 'react'

const PASSOS = [
  {
    icone: '👋',
    titulo: 'Bem-vindo ao Saldo Verde!',
    descricao: 'Este tutorial vai guiá-lo pelo sistema em poucos passos. Você aprenderá a cadastrar pessoas, classificações, registrar movimentações financeiras e usar os recursos de Inteligência Artificial.',
    dica: null,
  },
  {
    icone: '🗂️',
    titulo: 'Navegação pela Sidebar',
    descricao: 'O menu lateral esquerdo é o ponto de partida para todas as funcionalidades do sistema. Ele está dividido em duas seções:',
    lista: [
      '📁 IA — Nota Fiscal e Consulta IA (requer chave Gemini)',
      '📋 Cadastros — Pessoas, Classificação e Contas',
    ],
    dica: 'Clique em qualquer item do menu para navegar entre as telas.',
  },
  {
    icone: '👥',
    titulo: 'Manter Pessoas',
    descricao: 'Cadastre todos os envolvidos nas movimentações financeiras. Existem três tipos de pessoa:',
    lista: [
      '🏭 Fornecedor — Empresa ou pessoa que fornece produtos/serviços',
      '🛒 Cliente — Quem compra ou recebe os produtos/serviços',
      '🧾 Faturado — Responsável pelo pagamento da nota fiscal',
    ],
    dica: 'Use o botão "Todos" para ver todos os cadastros ativos, ou "Buscar" para filtrar por nome ou CPF/CNPJ.',
  },
  {
    icone: '🏷️',
    titulo: 'Manter Classificação',
    descricao: 'Classifique suas movimentações financeiras em categorias para melhor controle:',
    lista: [
      '📉 Despesa — Gastos da empresa (ex: Insumos Agrícolas, Combustível)',
      '📈 Receita — Entradas financeiras (ex: Venda de Grãos, Aluguel)',
    ],
    dica: 'Você pode criar classificações personalizadas além das já cadastradas no sistema.',
  },
  {
    icone: '💰',
    titulo: 'Manter Contas',
    descricao: 'Registre todas as movimentações financeiras da empresa:',
    lista: [
      '💸 A Pagar — Despesas e pagamentos a fornecedores',
      '💵 A Receber — Receitas e cobranças de clientes',
    ],
    dica: 'Cada conta pode ter várias parcelas. Preencha as datas de vencimento e valores de cada parcela ao criar uma conta.',
  },
  {
    icone: '🔑',
    titulo: 'Configurar a Chave API',
    descricao: 'Para usar os recursos de Inteligência Artificial (Upload de PDF e Consulta IA), é necessário configurar uma chave da API Google Gemini.',
    lista: [
      '1. Clique no ícone de chave no rodapé da sidebar',
      '2. Acesse aistudio.google.com/apikey para obter sua chave gratuita',
      '3. Cole a chave no campo e clique em "Salvar Chave"',
    ],
    dica: 'O ícone fica verde quando a chave está ativa e cinza quando não está configurada.',
  },
  {
    icone: '📄',
    titulo: 'Upload de Nota Fiscal',
    descricao: 'Faça o upload de notas fiscais em PDF e deixe a IA extrair automaticamente todas as informações:',
    lista: [
      '1. Clique em "Nota Fiscal" no menu lateral',
      '2. Arraste ou selecione um arquivo PDF',
      '3. Aguarde a extração automática dos dados',
      '4. Revise as informações e clique em "Salvar no Banco"',
    ],
    dica: 'A IA tenta usar o Gemini primeiro, com fallback automático para Claude e OpenAI.',
  },
  {
    icone: '🤖',
    titulo: 'Consulta IA',
    descricao: 'Faça perguntas em linguagem natural sobre seus dados financeiros e receba respostas inteligentes:',
    lista: [
      '💬 RAG Simples — Busca nos 20 registros mais recentes',
      '🔍 RAG Embeddings — Busca semântica em toda a base de dados',
    ],
    dica: 'Exemplos de perguntas: "Qual o total gasto com insumos?" ou "Quais são os fornecedores com mais movimentações?"',
  },
  {
    icone: '✅',
    titulo: 'Tudo pronto!',
    descricao: 'Você já sabe o suficiente para usar o Saldo Verde. Sempre que precisar rever este tutorial, clique em "Tutorial" no menu lateral.',
    dica: 'Dúvidas? Consulte o manual completo ou entre em contato com o suporte.',
  },
]

export default function Tutorial({ onFechar }) {
  const [passo, setPasso] = useState(0)

  const atual     = PASSOS[passo]
  const ehUltimo  = passo === PASSOS.length - 1
  const ehPrimeiro = passo === 0
  const progresso = ((passo + 1) / PASSOS.length) * 100

  function avancar() {
    if (ehUltimo) { onFechar(); return }
    setPasso(p => p + 1)
  }

  function voltar() {
    if (!ehPrimeiro) setPasso(p => p - 1)
  }

  return (
    <div className="tutorial-overlay" onClick={onFechar}>
      <div className="tutorial-card" onClick={e => e.stopPropagation()}>

        {/* Cabeçalho */}
        <div className="tutorial-topo">
          <span className="tutorial-contador">Passo {passo + 1} de {PASSOS.length}</span>
          <button className="tutorial-pular" onClick={onFechar}>Pular tutorial ✕</button>
        </div>

        {/* Barra de progresso */}
        <div className="tutorial-progresso-barra">
          <div className="tutorial-progresso-fill" style={{ width: `${progresso}%` }} />
        </div>

        {/* Conteúdo */}
        <div className="tutorial-corpo">
          <div className="tutorial-icone">{atual.icone}</div>
          <h2 className="tutorial-titulo">{atual.titulo}</h2>
          <p className="tutorial-descricao">{atual.descricao}</p>

          {atual.lista && (
            <ul className="tutorial-lista">
              {atual.lista.map((item, i) => (
                <li key={i} className="tutorial-lista-item">{item}</li>
              ))}
            </ul>
          )}

          {atual.dica && (
            <div className="tutorial-dica">
              <span className="tutorial-dica-icone">💡</span>
              <span>{atual.dica}</span>
            </div>
          )}
        </div>

        {/* Indicadores de passo */}
        <div className="tutorial-dots">
          {PASSOS.map((_, i) => (
            <button
              key={i}
              className={`tutorial-dot ${i === passo ? 'tutorial-dot--ativo' : ''} ${i < passo ? 'tutorial-dot--feito' : ''}`}
              onClick={() => setPasso(i)}
              aria-label={`Ir para passo ${i + 1}`}
            />
          ))}
        </div>

        {/* Botões de navegação */}
        <div className="tutorial-rodape">
          <button className="tutorial-btn-voltar" onClick={voltar} disabled={ehPrimeiro}>
            ← Anterior
          </button>
          <button className="tutorial-btn-avancar" onClick={avancar}>
            {ehUltimo ? 'Concluir ✓' : 'Próximo →'}
          </button>
        </div>

      </div>
    </div>
  )
}
