import { useState, useEffect, useRef } from 'react'

const PASSOS = [
  {
    titulo: 'Bem-vindo ao Saldo Verde!',
    descricao: 'Este tutorial vai guiá-lo pelo sistema em poucos passos. Você aprenderá a cadastrar pessoas, classificações, registrar movimentações financeiras e usar os recursos de Inteligência Artificial.',
    dica: 'Use "Próximo" ou clique nos pontos abaixo para navegar entre os passos.',
    alvo: null,
  },
  {
    titulo: 'Menu de Navegação',
    descricao: 'A sidebar à esquerda contém todos os acessos do sistema, divididos em duas seções.',
    lista: [
      'IA — Nota Fiscal e Consulta IA (requer chave Gemini)',
      'Cadastros — Pessoas, Classificação e Contas',
    ],
    dica: 'Clique em qualquer item do menu para acessar a funcionalidade.',
    alvo: '[data-tutorial="sidebar"]',
  },
  {
    titulo: 'Pessoas',
    descricao: 'Cadastre todos os envolvidos nas movimentações financeiras. Existem três tipos de pessoa:',
    lista: [
      'Fornecedor — Empresa ou pessoa que fornece produtos ou serviços',
      'Cliente — Quem compra ou recebe os produtos',
      'Faturado — Responsável pelo pagamento da nota fiscal',
    ],
    dica: 'Use "Todos" para ver todos os cadastros ativos ou "Buscar" para filtrar por nome.',
    alvo: '[data-tutorial="nav-pessoas"]',
  },
  {
    titulo: 'Classificação',
    descricao: 'Classifique suas movimentações financeiras em categorias para melhor controle:',
    lista: [
      'Despesa — Gastos da empresa (ex: Insumos Agrícolas, Combustível)',
      'Receita — Entradas financeiras (ex: Venda de Grãos, Aluguel)',
    ],
    dica: 'Você pode criar classificações personalizadas além das já cadastradas.',
    alvo: '[data-tutorial="nav-classificacao"]',
  },
  {
    titulo: 'Contas',
    descricao: 'Registre todas as movimentações financeiras da empresa:',
    lista: [
      'A Pagar — Despesas e pagamentos a fornecedores',
      'A Receber — Receitas e cobranças de clientes',
    ],
    dica: 'Cada conta pode ter várias parcelas com datas de vencimento individuais.',
    alvo: '[data-tutorial="nav-contas"]',
  },
  {
    titulo: 'Configurar a Chave API',
    descricao: 'Para usar os recursos de Inteligência Artificial é necessário informar uma chave da API Google Gemini a cada novo login.',
    lista: [
      '1. Clique no ícone de chave no rodapé da sidebar (ou acesse Nota Fiscal/Consulta IA)',
      '2. Acesse aistudio.google.com/apikey para obter sua chave gratuita',
      '3. Cole a chave no campo e clique em "Salvar Chave"',
    ],
    dica: 'O ícone fica verde quando a chave está ativa. Ao sair do sistema, a chave é esquecida e precisa ser informada novamente no próximo login.',
    alvo: '[data-tutorial="chave-btn"]',
  },
  {
    titulo: 'Upload de Nota Fiscal',
    descricao: 'Faça upload de notas fiscais em PDF e a IA extrai automaticamente todas as informações:',
    lista: [
      '1. Clique em "Nota Fiscal" no menu lateral',
      '2. Arraste ou selecione um arquivo PDF',
      '3. Aguarde a extração automática dos dados',
      '4. Revise as informações — os dados são salvos automaticamente no banco',
    ],
    dica: 'Necessário ter a chave Gemini configurada antes de usar este recurso.',
    alvo: '[data-tutorial="nav-upload"]',
  },
  {
    titulo: 'Consulta IA',
    descricao: 'Faça perguntas em linguagem natural sobre seus dados financeiros e receba respostas inteligentes:',
    lista: [
      'RAG Simples — ideal para contas, somas e relatórios precisos',
      'RAG Embeddings — busca inteligente pelo assunto ou significado das palavras',
    ],
    dica: 'Exemplo: "Qual o total gasto com insumos?" ou "O que foi comprado para controle de pragas?"',
    alvo: '[data-tutorial="nav-consulta"]',
  },
  {
    titulo: 'Tudo pronto!',
    descricao: 'Você já sabe o suficiente para usar o Saldo Verde. Bom trabalho!',
    dica: null,
    alvo: null,
  },
]

export default function Tutorial({ onFechar }) {
  const [passo, setPasso] = useState(0)
  const cardRef = useRef(null)
  const [geo, setGeo] = useState(null)

  const atual      = PASSOS[passo]
  const ehUltimo   = passo === PASSOS.length - 1
  const ehPrimeiro = passo === 0
  const progresso  = ((passo + 1) / PASSOS.length) * 100

  function calcular() {
    if (!atual.alvo || !cardRef.current) { setGeo(null); return }
    const el = document.querySelector(atual.alvo)
    if (!el) { setGeo(null); return }

    const elRect   = el.getBoundingClientRect()
    const cardRect = cardRef.current.getBoundingClientRect()

    const pad = 6
    const sx = elRect.left   - pad
    const sy = elRect.top    - pad
    const sw = elRect.width  + pad * 2
    const sh = elRect.height + pad * 2

    // Arrow: from left edge of card toward right side of spotlight rect
    const ax1 = cardRect.left - 8
    const ay1 = cardRect.top  + cardRect.height / 2
    const ax2 = sx + sw + 6
    const ay2 = sy + sh / 2
    // Quadratic bezier: start horizontal at card height, then curve to target
    const qx = ax1 - (ax1 - ax2) / 2
    const qy = ay1

    setGeo({ sx, sy, sw, sh, ax1, ay1, ax2, ay2, qx, qy })
  }

  useEffect(() => {
    const t = setTimeout(calcular, 80)
    window.addEventListener('resize', calcular)
    return () => { clearTimeout(t); window.removeEventListener('resize', calcular) }
  }, [passo])

  function avancar() { if (ehUltimo) { onFechar(); return } setPasso(p => p + 1) }
  function voltar()  { if (!ehPrimeiro) setPasso(p => p - 1) }

  return (
    <div className="tutorial-overlay">

      {/* SVG: dark backdrop with spotlight cutout + dashed arrow */}
      <svg className="tutorial-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <mask id="tmask">
            <rect width="100%" height="100%" fill="white" />
            {geo && (
              <rect x={geo.sx} y={geo.sy} width={geo.sw} height={geo.sh} rx="8" fill="black" />
            )}
          </mask>
          <marker id="tarrow" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto">
            <polygon points="0 0, 9 3.5, 0 7" fill="#22c55e" />
          </marker>
        </defs>

        {/* Dark overlay with spotlight hole */}
        <rect width="100%" height="100%" fill="rgba(0,0,0,0.65)" mask="url(#tmask)" />

        {/* Green ring around the highlighted element */}
        {geo && (
          <rect
            x={geo.sx} y={geo.sy} width={geo.sw} height={geo.sh} rx="8"
            fill="none" stroke="#22c55e" strokeWidth="2.5" opacity="0.9"
          />
        )}

        {/* Dashed arrow from card to spotlight */}
        {geo && (
          <path
            d={`M ${geo.ax1} ${geo.ay1} Q ${geo.qx} ${geo.qy} ${geo.ax2} ${geo.ay2}`}
            fill="none" stroke="#22c55e" strokeWidth="2.5"
            strokeDasharray="8 5" markerEnd="url(#tarrow)"
          />
        )}
      </svg>

      {/* Tutorial card */}
      <div
        ref={cardRef}
        className={`tutorial-card ${atual.alvo ? 'tutorial-card--lateral' : 'tutorial-card--centro'}`}
        onClick={e => e.stopPropagation()}
      >

        <div className="tutorial-topo">
          <span className="tutorial-contador">Passo {passo + 1} de {PASSOS.length}</span>
          <button className="tutorial-pular" onClick={onFechar}>Pular tutorial ✕</button>
        </div>

        <div className="tutorial-progresso-barra">
          <div className="tutorial-progresso-fill" style={{ width: `${progresso}%` }} />
        </div>

        <div className="tutorial-corpo">
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
              <span className="tutorial-dica-label">Dica</span>
              <span>{atual.dica}</span>
            </div>
          )}
        </div>

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

        <div className="tutorial-rodape">
          <button className="tutorial-btn-voltar" onClick={voltar} disabled={ehPrimeiro}>
            ← Anterior
          </button>
          <button className="tutorial-btn-avancar" onClick={avancar}>
            {ehUltimo ? 'Concluir' : 'Próximo →'}
          </button>
        </div>

      </div>
    </div>
  )
}
