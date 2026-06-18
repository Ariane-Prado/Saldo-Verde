from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import unicodedata

def _c(texto):
    """Converte para latin-1 seguro, substituindo caracteres especiais pelos mais proximos."""
    normalizado = unicodedata.normalize('NFKD', str(texto))
    return normalizado.encode('latin-1', errors='replace').decode('latin-1')

VERDE = (22, 163, 74)
VERDE_CLARO = (240, 253, 244)
VERDE_TEXTO = (20, 83, 45)
VERMELHO_BG = (254, 242, 242)
VERMELHO_TEXTO = (153, 27, 27)
CINZA_BG = (248, 248, 248)
CINZA_BORDA = (200, 200, 200)


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 6, _c("Saldo Verde - Documentacao Tecnica | Etapa 3: RAG"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(*CINZA_BORDA)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, _c(f"Pagina {self.page_no()}"), align="C")

    def sec(self, n, titulo):
        self.ln(5)
        self.set_fill_color(*VERDE)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, _c(f"  {n}. {titulo}"), fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def sub(self, titulo):
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*VERDE)
        self.cell(0, 7, _c(titulo), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def txt(self, texto):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, _c(texto))
        self.ln(1)

    def box(self, texto, bg=VERDE_CLARO, fg=VERDE_TEXTO):
        w = self.epw
        self.set_fill_color(*bg)
        self.set_draw_color(*VERDE)
        self.set_text_color(*fg)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(w, 5.5, _c(texto), border=1, fill=True)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.ln(2)

    def code(self, texto):
        self.set_fill_color(*CINZA_BG)
        self.set_draw_color(*CINZA_BORDA)
        self.set_text_color(40, 40, 40)
        self.set_font("Courier", "", 7.5)
        self.multi_cell(self.epw, 4.5, _c(texto), border=1, fill=True)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.ln(2)

    def erro_box(self, erro, solucao):
        w = self.epw
        self.set_fill_color(*VERMELHO_BG)
        self.set_draw_color(*CINZA_BORDA)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*VERMELHO_TEXTO)
        self.multi_cell(w, 5.5, _c(f"ERRO: {erro}"), border="TLR", fill=True)
        self.set_fill_color(*VERDE_CLARO)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*VERDE_TEXTO)
        self.multi_cell(w, 5.5, _c(f"SOLUCAO: {solucao}"), border="BLR", fill=True)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.ln(3)

    def tabrow(self, cols, widths, header=False):
        if header:
            self.set_fill_color(*VERDE)
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 8)
        else:
            self.set_fill_color(250, 250, 250)
            self.set_text_color(30, 30, 30)
            self.set_font("Helvetica", "", 8)
        for i, (col, w) in enumerate(zip(cols, widths)):
            last = (i == len(cols) - 1)
            nx = XPos.LMARGIN if last else XPos.RIGHT
            ny = YPos.NEXT if last else YPos.TOP
            self.cell(w, 7, _c(col), border=1, fill=header, new_x=nx, new_y=ny)
        self.set_text_color(0, 0, 0)


# ─────────────────────────────────────────────────────────────────────────────
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()

# CAPA
pdf.ln(18)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(*VERDE)
pdf.cell(0, 14, _c("Saldo Verde"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(70, 70, 70)
pdf.cell(0, 8, _c("Documentacao Tecnica - Etapa 3: Consulta com RAG"),
         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(4)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 6, _c("Flask + PostgreSQL + React 19 + Gemini 2.5 Flash"),
         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(16)
pdf.set_draw_color(*VERDE)
pdf.set_line_width(0.8)
pdf.line(25, pdf.get_y(), 185, pdf.get_y())
pdf.set_line_width(0.2)
pdf.set_draw_color(0, 0, 0)
pdf.ln(12)

pdf.set_font("Helvetica", "B", 11)
pdf.set_text_color(30, 30, 30)
pdf.cell(0, 8, _c("Conteudo deste documento:"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(60, 60, 60)
for item in [
    "1. Visao Geral do Projeto",
    "2. O que e RAG (Retrieval-Augmented Generation)",
    "3. RAG Simples - Algoritmo e Logica",
    "4. RAG Embeddings - Algoritmo e Logica",
    "5. Modal de Chave API - Problema e Solucao",
    "6. Erros Encontrados e Como Foram Resolvidos",
    "7. Diferenca Pratica entre os Modos RAG",
    "8. Banco de Dados - Schema e Evolucao",
    "9. Como Explicar em uma Prova Tecnica",
]:
    pdf.cell(8)
    pdf.cell(0, 7, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ── 1 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(1, "Visao Geral do Projeto")
pdf.txt(
    "O Saldo Verde e um sistema de gestao financeira agricola com arquitetura de tres camadas: "
    "backend em Flask (Python), banco de dados PostgreSQL e frontend em React 19. "
    "Todo o ambiente roda em Docker com docker-compose."
)
pdf.sub("Stack tecnologica:")
pdf.txt(
    "- Backend: Python 3.13 + Flask + psycopg2 + Google GenAI SDK\n"
    "- Banco: PostgreSQL 17\n"
    "- Frontend: React 19 + Vite\n"
    "- Servidor: Gunicorn (1 worker)\n"
    "- Infraestrutura: Docker + docker-compose\n"
    "- LLM: Gemini 2.5 Flash (Google)"
)
pdf.sub("Tabelas do banco:")
pdf.txt(
    "- PESSOAS: fornecedores, clientes e faturados\n"
    "- CLASSIFICACAO: categorias de despesa ou receita\n"
    "- MOVIMENTOCONTAS: cada nota fiscal ou lancamento financeiro\n"
    "- PARCELACONTAS: parcelas de cada movimento"
)

# ── 2 ─────────────────────────────────────────────────────────────────────────
pdf.sec(2, "O que e RAG (Retrieval-Augmented Generation)")
pdf.txt(
    "RAG e uma tecnica que melhora as respostas de LLMs combinando busca de dados reais "
    "com geracao de texto. Sem RAG, a IA responderia com conhecimento generico e inventaria "
    "numeros. Com RAG, ela so usa o que existe no banco de dados do sistema."
)
pdf.box(
    "Fluxo RAG:\n"
    "  Pergunta do usuario\n"
    "  -> RETRIEVAL:    busca registros relevantes no banco de dados\n"
    "  -> AUGMENTATION: monta um contexto com os dados encontrados\n"
    "  -> GENERATION:   envia contexto + pergunta ao LLM (Gemini)\n"
    "  -> Resposta elaborada com base em dados reais do sistema"
)

# ── 3 ─────────────────────────────────────────────────────────────────────────
pdf.sec(3, "RAG Simples - Algoritmo e Logica")
pdf.txt(
    "A forma mais direta de RAG. O algoritmo:\n\n"
    "1. Busca os 20 registros mais recentes do banco (ORDER BY data_emissao DESC LIMIT 20)\n"
    "2. Formata cada registro como uma linha de texto legivel\n"
    "3. Concatena todas as linhas como contexto\n"
    "4. Envia contexto + pergunta ao Gemini\n"
    "5. Retorna a resposta gerada"
)
pdf.sub("Codigo simplificado:")
pdf.code(
    "def consultar_rag_simples(pergunta):\n"
    "    registros = _buscar_registros(limit=20)   # 20 mais recentes\n"
    "    contexto  = '\\n'.join(_formatar_linha(r) for r in registros)\n"
    "    return _chamar_llm(contexto, pergunta)\n"
    "\n"
    "def _chamar_llm(contexto, pergunta):\n"
    "    prompt = f'DADOS DO SISTEMA:\\n{contexto}\\nPERGUNTA: {pergunta}'\n"
    "    response = client.models.generate_content(\n"
    "        model='gemini-2.5-flash', contents=[prompt])\n"
    "    return response.text"
)
pdf.box(
    "Limitacao: so ve os 20 registros mais recentes. Se o dado perguntado esta em um\n"
    "registro antigo, a IA responde 'nao encontrei dados' mesmo que exista no banco."
)

# ── 4 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(4, "RAG Embeddings - Algoritmo e Logica")
pdf.txt(
    "Mais sofisticado: busca TODOS os registros e usa similaridade matematica para "
    "encontrar os mais relevantes para a pergunta. Implementado com vetorizacao TF "
    "(Term Frequency) + cosine similarity usando apenas bibliotecas padrao do Python."
)
pdf.sub("Passo a passo:")
pdf.txt(
    "1. Busca TODOS os registros (sem LIMIT)\n"
    "2. Converte cada registro em um vetor de palavras (bag-of-words / TF)\n"
    "3. Converte a pergunta do usuario em um vetor de palavras\n"
    "4. Calcula cosine similarity entre a pergunta e cada registro\n"
    "5. Seleciona os 5 com maior similaridade (top_k=5)\n"
    "6. Envia esses 5 como contexto ao Gemini\n"
    "7. Retorna a resposta"
)
pdf.sub("O que e cosine similarity?")
pdf.txt(
    "Mede o angulo entre dois vetores de palavras. Se a pergunta contem 'defensivos agricolas'\n"
    "e um registro tambem tem essas palavras, o angulo e pequeno (resultado proximo a 1.0).\n"
    "Se nao tem nenhuma palavra em comum, o resultado e 0.0."
)
pdf.sub("Formula e codigo:")
pdf.code(
    "# Cada texto vira um dicionario {palavra: frequencia}\n"
    "def _tf_vetor(texto):\n"
    "    tokens = re.findall(r'\\w+', texto.lower())\n"
    "    return Counter(tokens)\n"
    "\n"
    "# cos(A,B) = (A . B) / (|A| * |B|)\n"
    "def _cosine_similarity_tf(v1, v2):\n"
    "    comum    = set(v1.keys()) & set(v2.keys())   # palavras em comum\n"
    "    num      = sum(v1[w] * v2[w] for w in comum) # produto escalar\n"
    "    norma1   = math.sqrt(sum(c**2 for c in v1.values()))\n"
    "    norma2   = math.sqrt(sum(c**2 for c in v2.values()))\n"
    "    if not norma1 or not norma2: return 0.0\n"
    "    return num / (norma1 * norma2)  # resultado: 0.0 a 1.0\n"
    "\n"
    "def consultar_rag_embeddings(pergunta, top_k=5):\n"
    "    registros = _buscar_registros(limit=None)     # TODOS\n"
    "    textos    = [_formatar_linha(r) for r in registros]\n"
    "    vp        = _tf_vetor(pergunta)\n"
    "    scores    = [_cosine_similarity_tf(vp, _tf_vetor(t)) for t in textos]\n"
    "    top       = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]\n"
    "    contexto  = '\\n'.join(textos[i] for i in top)\n"
    "    return _chamar_llm(contexto, pergunta)"
)
pdf.box(
    "Por que nao usar a API de embeddings do Google?\n"
    "Tentamos usar text-embedding-004 mas retornou erro 404 nas versoes v1beta e v1 da API.\n"
    "Solucao: vetorizacao local com Python puro, sem dependencia de API externa.\n"
    "Funciona bem para dados tabulares e textuais como os do sistema."
)

# ── 5 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(5, "Modal de Chave API - Problema e Solucao")
pdf.sub("O problema:")
pdf.txt(
    "A chave da API do Gemini nao pode ser commitada no git (risco de seguranca).\n"
    "Usar .env exigiria configuracao manual antes de rodar o Docker.\n"
    "Solucao: modal no frontend que solicita a chave ao iniciar o sistema."
)
pdf.sub("Como funciona:")
pdf.txt(
    "1. Ao abrir o sistema, um modal pede a chave Gemini ao usuario\n"
    "2. O frontend faz POST /configurar-chave com a chave no body JSON\n"
    "3. O backend armazena em memoria (modulo config.py, dicionario _runtime)\n"
    "4. Todas as chamadas ao Gemini buscam a chave desse dicionario\n"
    "5. A chave some ao reiniciar o container (nunca vai para o disco ou git)"
)
pdf.code(
    "# backend/config.py\n"
    "_runtime = {}\n"
    "\n"
    "def set_gemini_key(chave):\n"
    "    _runtime['GEMINI_API_KEY'] = chave\n"
    "\n"
    "def get_gemini_key():\n"
    "    return _runtime.get('GEMINI_API_KEY')\n"
    "\n"
    "# Em qualquer modulo que chama Gemini:\n"
    "def _get_gemini_client():\n"
    "    global gemini_client\n"
    "    chave = config.get_gemini_key() or GEMINI_API_KEY  # modal tem prioridade\n"
    "    if gemini_client is None and chave:\n"
    "        gemini_client = genai.Client(api_key=chave)\n"
    "    return gemini_client"
)
pdf.sub("Por que Gunicorn com 1 worker?")
pdf.txt(
    "Com multiplos workers (processos), cada processo tem sua propria memoria isolada.\n"
    "A chave salva no worker 1 nao existe no worker 2 — requisicoes no worker 2 falhavam.\n"
    "Com 1 worker, todas as requisicoes compartilham a mesma memoria."
)
pdf.code(
    "# backend/Dockerfile\n"
    "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"--workers\", \"1\", \"app:app\"]"
)

# ── 6 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(6, "Erros Encontrados e Como Foram Resolvidos")

pdf.erro_box(
    "'Nenhuma API disponivel, configure ao menos uma chave no .env'",
    "consulta_dados.py importava GEMINI_API_KEY como constante no nivel do modulo\n"
    "(sempre None sem .env). Corrigido verificando em tempo de execucao:\n"
    "  chave = config.get_gemini_key() or GEMINI_API_KEY"
)
pdf.erro_box(
    "[DOM] Password field is not contained in a form",
    "O <input type='password'> estava fora de uma tag <form>.\n"
    "Browsers exigem isso por seguranca. Corrigido envolvendo em:\n"
    "  <form onSubmit={confirmar}>...</form>"
)
pdf.erro_box(
    "'NoneType' object has no attribute 'models' (erro HTTP 500)",
    "Gunicorn rodava com 2 workers. A chave era salva na memoria do worker 1\n"
    "mas requisicoes podiam cair no worker 2 (sem a chave).\n"
    "Corrigido: Dockerfile alterado para --workers 1."
)
pdf.erro_box(
    "404 NOT_FOUND: models/text-embedding-004 not found (v1beta e v1)",
    "O modelo de embeddings do Google nao estava disponivel nas versoes da API usadas.\n"
    "Solucao: substituir completamente por vetorizacao TF local (bag-of-words + cosine)\n"
    "usando re, math e collections.Counter — sem dependencia de API externa."
)
pdf.erro_box(
    "Ambos RAGs respondiam 'Nao ha dados de DEFENSIVOS AGRICOLAS'",
    "_buscar_registros() tinha LIMIT 20 e era compartilhada pelos dois modos.\n"
    "RAG Embeddings re-ranqueava os mesmos 20 do RAG Simples.\n"
    "Corrigido: RAG Embeddings chama _buscar_registros(limit=None) para buscar TUDO\n"
    "e so entao filtra os 5 mais relevantes por cosine similarity."
)
pdf.erro_box(
    "UPDATE PESSOAS viola check constraint pessoas_tipo_check",
    "Tentamos UPDATE antes de dropar a constraint antiga. Ordem correta:\n"
    "  1. ALTER TABLE PESSOAS DROP CONSTRAINT pessoas_tipo_check;\n"
    "  2. UPDATE PESSOAS SET tipo = 'FORNECEDOR' WHERE tipo = 'CLIENTE-FORNECEDOR';\n"
    "  3. ALTER TABLE PESSOAS ADD CONSTRAINT pessoas_tipo_check\n"
    "        CHECK (tipo IN ('FORNECEDOR', 'CLIENTE', 'FATURADO'));"
)

# ── 7 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(7, "Diferenca Pratica entre os Modos RAG")
pdf.txt(
    "Com poucas linhas no banco ambos dao respostas iguais. "
    "A diferenca aparece com volume (100+ registros variados)."
)

W = [42, 72, 72]
pdf.tabrow(["Criterio", "RAG Simples", "RAG Embeddings"], W, header=True)
for row in [
    ("O que manda pra IA",   "20 registros mais recentes",  "5 mais similares a pergunta"),
    ("Busca no banco",       "LIMIT 20 ORDER BY data DESC", "Sem LIMIT - todos os registros"),
    ("Filtragem",            "Nenhuma, envia tudo",         "Cosine similarity TF bag-of-words"),
    ("Bom para",             "Resumo do periodo recente",   "Perguntas especificas por tema"),
    ("Fraqueza",             "Nao encontra dados antigos",  "Depende de palavras na pergunta"),
    ("Custo de tokens",      "Alto (mais contexto)",        "Baixo (contexto enxuto)"),
]:
    pdf.tabrow(row, W)

pdf.ln(4)
pdf.box(
    "Exemplo real que demonstrou a diferenca:\n\n"
    "Pergunta: 'total gasto com defensivos agricolas?'\n\n"
    "RAG Simples   -> 'Nao ha dados de DEFENSIVOS AGRICOLAS nos registros fornecidos'\n"
    "  (os registros de defensivos nao estavam entre os 20 mais recentes)\n\n"
    "RAG Embeddings -> 'Total gasto com defensivos agricolas: R$ 24.039,66'\n"
    "  (encontrou todos os registros de defensivos nos 200 do banco por similaridade)"
)

# ── 8 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(8, "Banco de Dados - Schema e Evolucao")

pdf.sub("Tabela PESSOAS - mudanca realizada para a Etapa 4:")
pdf.code(
    "-- Antes (so 2 tipos):\n"
    "tipo VARCHAR(20) CHECK (tipo IN ('CLIENTE-FORNECEDOR', 'FATURADO'))\n"
    "\n"
    "-- Depois (3 tipos separados para o CRUD da etapa 4):\n"
    "tipo VARCHAR(20) CHECK (tipo IN ('FORNECEDOR', 'CLIENTE', 'FATURADO'))\n"
    "\n"
    "-- Migracao executada no banco (ordem obrigatoria):\n"
    "ALTER TABLE PESSOAS DROP CONSTRAINT pessoas_tipo_check;\n"
    "UPDATE PESSOAS SET tipo = 'FORNECEDOR' WHERE tipo = 'CLIENTE-FORNECEDOR';\n"
    "ALTER TABLE PESSOAS ADD CONSTRAINT pessoas_tipo_check\n"
    "    CHECK (tipo IN ('FORNECEDOR', 'CLIENTE', 'FATURADO'));"
)

pdf.sub("Relacao entre as tabelas:")
pdf.code(
    "PESSOAS          (id, tipo[FORNECEDOR|CLIENTE|FATURADO], razao_social, cpf_cnpj, ativo)\n"
    "CLASSIFICACAO    (id, tipo[DESPESA|RECEITA], descricao, ativo)\n"
    "MOVIMENTOCONTAS  (id, tipo[APAGAR|ARECEBER], id_fornecedor->PESSOAS, id_faturado->PESSOAS,\n"
    "                  id_classificacao->CLASSIFICACAO, valor_total, data_emissao, ativo)\n"
    "PARCELACONTAS    (id, id_movimento->MOVIMENTOCONTAS, identificacao,\n"
    "                  data_vencimento, valor, ativo)"
)

pdf.sub("Por que ativo=TRUE em todas as tabelas?")
pdf.txt(
    "Exclusao logica (soft delete): em vez de DELETE, setamos ativo=FALSE.\n"
    "Isso preserva o historico financeiro e permite auditoria.\n"
    "Todas as queries filtram WHERE ativo = TRUE."
)

# ── 9 ─────────────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.sec(9, "Como Explicar em uma Prova Tecnica")

pdf.sub("P: O que e RAG e por que foi usado?")
pdf.box(
    "RAG (Retrieval-Augmented Generation) combina busca em banco de dados com geracao de texto\n"
    "por LLM. Foi usado porque o Gemini nao conhece os dados financeiros do sistema.\n"
    "Sem RAG a IA inventaria numeros. Com RAG ela so responde com base em dados reais do PostgreSQL."
)

pdf.sub("P: Qual a diferenca entre RAG Simples e RAG Embeddings?")
pdf.box(
    "RAG Simples pega os N registros mais recentes e envia todos como contexto.\n"
    "Simples de implementar, mas limitado: nao encontra dados antigos ou de categorias especificas\n"
    "que nao estejam nos N mais recentes.\n\n"
    "RAG Embeddings varre todos os registros, calcula similaridade matematica (cosine similarity)\n"
    "entre cada registro e a pergunta, e seleciona apenas os mais relevantes.\n"
    "Resultado: contexto focado, respostas mais precisas para perguntas especificas."
)

pdf.sub("P: Como funciona cosine similarity?")
pdf.box(
    "Cada texto e convertido em um vetor onde cada dimensao e uma palavra e o valor e\n"
    "quantas vezes ela aparece (bag-of-words).\n\n"
    "Formula: cos(A,B) = (A . B) / (|A| x |B|)\n\n"
    "Onde A.B e o produto escalar (soma dos produtos das frequencias das palavras em comum)\n"
    "e |A|, |B| sao as normas euclidianas dos vetores.\n"
    "Resultado: 0.0 (nada em comum) a 1.0 (textos identicos)."
)

pdf.sub("P: Por que a chave API fica na memoria e nao no .env?")
pdf.box(
    "Armazenar chaves API no git e falha grave de seguranca. O .env resolve localmente\n"
    "mas exige configuracao antes de subir o Docker.\n\n"
    "Solucao: modal no frontend coleta a chave em tempo de execucao. O backend armazena\n"
    "em um dicionario Python em memoria. A chave nunca toca o disco ou o git.\n"
    "Some automaticamente ao reiniciar o container."
)

pdf.sub("P: Por que Gunicorn com 1 worker?")
pdf.box(
    "Multiplos workers = multiplos processos com memorias isoladas.\n"
    "A chave salva no worker 1 nao existe no worker 2, causando erro 500 em 50% das requisicoes.\n"
    "Com 1 worker todas as requisicoes compartilham a mesma memoria.\n"
    "Tradeoff: menor throughput, mas suficiente para o caso de uso academico."
)

pdf.sub("P: O que e exclusao logica (soft delete)?")
pdf.box(
    "Em vez de DELETE, setamos ativo=FALSE no registro.\n"
    "Vantagens: historico financeiro preservado, possivel desfazer exclusao, rastreabilidade.\n"
    "Todas as queries filtram WHERE ativo = TRUE, entao registros inativos sao ignorados."
)

saida = "Saldo_Verde_Documentacao_RAG.pdf"
pdf.output(saida)
print(f"PDF gerado: {os.path.abspath(saida)}")
