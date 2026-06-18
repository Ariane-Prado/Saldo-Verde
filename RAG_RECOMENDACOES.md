# Recomendações — Pipeline RAG (`backend/agents/rag/consulta_rag.py`)

Revisão técnica do pipeline RAG (busca semântica via FAISS + agregação SQL + Gemini).
Lista consolidada de alterações recomendadas, organizadas por severidade.

---

## Críticas

- [ ] **1. Verificar nome do modelo de embedding**
  `backend/agents/rag/consulta_rag.py:26`
  `_EMBED_MODEL = "models/gemini-embedding-2"` não corresponde a nenhum ID conhecido da API Gemini. O `_EMBED_DIM = 3072` (linha 27) coincide com o padrão do modelo `gemini-embedding-001`, sugerindo que o nome correto seria esse. Confirmar com uma chamada real e corrigir se necessário.

- [ ] **2. Remover falha silenciosa em `_get_vector_store`**
  `backend/agents/rag/consulta_rag.py:538-540`
  O `except Exception` genérico engole qualquer erro de construção do índice (ex.: modelo de embedding inválido) e apenas loga `warning`. O modo "embeddings" degrada para "nenhum contexto" sem alerta visível. Trocar para log em nível `error` com stacktrace, ou expor um health-check que reporte o estado do índice.

- [ ] **3. Resolver estado global por processo (multi-worker)**
  `backend/agents/rag/consulta_rag.py:448-449`, `74-76`
  `_vector_store`, `_categorias_cache` e `gemini_client` são globais de módulo, protegidos só por `threading.Lock` (válido dentro de um processo). Se o deploy usar mais de um worker/instância, cada processo constrói seu próprio índice de forma independente — multiplica custo de embedding por N workers e pode servir respostas inconsistentes entre processos.
  **Ação prévia**: confirmar a topologia de deploy no Render (quantos workers/instâncias) antes de decidir a solução (armazenamento compartilhado, ex. pgvector, vs. fixar single-worker).

- [ ] **4. Corrigir deduplicação de parcelas no índice**
  `backend/agents/rag/consulta_rag.py:486-496`
  A deduplicação por `m.id` mantém apenas a primeira linha retornada pelo `JOIN` com `PARCELACONTAS`, descartando dados de parcelas adicionais (datas de vencimento e valores diferentes). Um movimento com 3 parcelas só tem a 1ª indexada. Agregar todas as parcelas no texto de embedding em vez de descartar.

- [ ] **5. Mitigar risco de prompt injection indireta**
  `backend/agents/rag/consulta_rag.py:640-644`
  O prompt final (`f"DADOS:\n{contexto}\n\nPERGUNTA: {pergunta}"`) não delimita nem instrui o modelo a tratar `DADOS` como conteúdo inerte. Campos como `descricao_itens`/`razao_social` podem ter origem em texto extraído de PDFs de terceiros (via agente de extração de notas fiscais). Adicionar delimitadores fortes (ex. tags `<dados>...</dados>`) e instrução explícita de não seguir instruções contidas nos dados.

- [ ] **6. Adicionar autenticação em rotas sensíveis**
  `backend/app.py:172-182`
  `/configurar-chave` e `/consultar` não têm nenhuma checagem de sessão/login. A chave Gemini é guardada em estado global de processo (`config._runtime`), compartilhado por todas as requisições concorrentes — qualquer cliente pode sobrescrevê-la para todos os usuários.

---

## Moderadas

- [ ] **7. Corrigir cobertura de `subset_ids` na busca FAISS**
  `backend/agents/rag/consulta_rag.py:577`
  `busca_k = top_k * 3` busca os vizinhos mais próximos *globalmente* e só depois filtra por `subset_ids`. Se os itens relevantes do subconjunto não estiverem entre os `3*top_k` vizinhos globais, nunca são considerados — mesmo sendo os únicos candidatos válidos. Buscar similaridade direto contra os vetores do subconjunto (ex. via `index.reconstruct` pelos IDs) em vez de filtrar um top-N global.

- [ ] **8. Preservar seções fixas no truncamento de contexto**
  `backend/agents/rag/consulta_rag.py:605-615`, `394-412`
  `_truncar_contexto` corta por linha a partir do início. Em `_buscar_contexto_agregado`, a seção "Top-5 menores NFs" é montada por último — conforme a base crescer, é a primeira a ser cortada, sem aviso ao LLM ou ao usuário. Garantir que seções fixas (total geral, top-5 maiores/menores) sejam preservadas, ou avisar explicitamente quando houver truncamento.

- [ ] **9. Invalidar cache de categorias**
  `backend/agents/rag/consulta_rag.py:74-94`
  `_categorias_cache` é carregado uma vez por processo e nunca invalidado. Renomear/criar uma classificação não reflete em runtime até reiniciar o processo.

- [ ] **10. Invalidar índice FAISS também no CRUD de Pessoas/Classificação**
  `backend/app.py:237-311`
  Apenas o CRUD de `/movimentos` chama `reset_vector_store()`. Renomear um fornecedor ou classificação deixa o índice FAISS com nomes desatualizados, enquanto o caminho de agregação SQL (que faz `JOIN` ao vivo) mostra o nome novo — gera contradição entre as duas seções do mesmo prompt.

- [ ] **11. Corrigir uso de `or` em campos monetários**
  `backend/agents/rag/consulta_rag.py:240`, `244-257`
  `r.get('valor_parcela') or '-'` trata um valor genuíno de `R$ 0,00` como falsy, exibindo `"-"` (parece dado ausente). Trocar por checagem explícita `is not None`.

- [ ] **12. Adicionar retry/backoff nas chamadas Gemini**
  `backend/agents/rag/consulta_rag.py:422-433`, `620-649`
  Sem retry para `embed_content`/`generate_content`. Qualquer rate limit ou erro transiente de rede vira erro 500 direto para o usuário. Adicionar retry com backoff exponencial (ex. biblioteca `tenacity`).

- [ ] **13. Erro claro quando cliente Gemini está ausente**
  `backend/agents/rag/consulta_rag.py:54-59`
  Sem chave configurada, `_get_gemini_client()` retorna `None` silenciosamente; a chamada seguinte falha com `AttributeError` genérico em vez de mensagem clara ("chave não configurada").

---

## Sugestões / priorizadas considerando volume esperado (~2000 notas em 6-12 meses)

- [ ] **14. Reduzir boilerplate no texto de embedding**
  `backend/agents/rag/consulta_rag.py:244-257`
  O texto gerado por `_formatar_para_embedding` é majoritariamente boilerplate repetido entre documentos ("Nota fiscal tipo X. Fornecedor: Y. Faturado para: Z..."), o que dilui a discriminação de similaridade entre documentos distintos. É a causa raiz mais provável de o threshold ter precisado ser baixado para 0.15 no banco pequeno — e o problema se agrava, não desaparece, conforme o volume cresce. Encurtar o texto para pares chave→valor sucintos, priorizando o conteúdo distintivo (itens, classificação).

- [ ] **15. Threshold relativo ao melhor score do batch**
  `backend/agents/rag/consulta_rag.py:585`
  Complementar (ou substituir) o corte absoluto `_SCORE_THRESHOLD = 0.15` por um corte relativo ao score do top-1 (ex. manter resultados com `score >= 0.85 * melhor_score`), para se adaptar automaticamente à distribuição de scores conforme o corpus cresce, sem precisar recalibrar manualmente.

- [ ] **16. Atualização incremental do índice FAISS**
  `backend/agents/rag/consulta_rag.py:478-515`
  Hoje qualquer escrita invalida o índice inteiro e a próxima consulta reembeda **todos** os registros (rebuild síncrono e bloqueante). Com 2000+ notas esperadas, isso passa a representar 10-40s de latência na primeira consulta após qualquer escrita. Trocar por `index.add`/`index.remove_ids` incrementais, reembedando apenas o registro alterado.

- [ ] **17. Conjunto de avaliação fixo**
  (processo, não código)
  Montar um conjunto de 10-15 perguntas com resposta/documento esperado conhecido, para re-testar objetivamente o threshold e a qualidade de recuperação conforme a base crescer — em vez de esperar "as respostas parecerem ruins" para descobrir que precisa recalibrar.

- [ ] **18. Connection pooling para PostgreSQL**
  `backend/database.py:8-15`
  Cada chamada abre uma nova conexão `psycopg2`. Uma única consulta RAG pode abrir 2-4 conexões curtas. Considerar um pool (ex. `psycopg2.pool` ou `pgbouncer`).

- [ ] **19. Logging de auditoria pergunta → contexto → resposta**
  `backend/agents/rag/consulta_rag.py` (geral)
  Hoje só há logs de depuração da recuperação (`[RANKING]`, `[PREFILTER]` etc.). Registrar o trio completo permite auditoria offline de qualidade/faithfulness.

- ~~**20. Migrar para índice HNSW**~~ — **descartado**: não necessário no volume esperado (2000 registros ainda é trivial para `IndexFlatIP`, busca exaustiva em microssegundos).

---

## Notas de contexto (da revisão)

- A decisão arquitetural de deixar o SQL fazer agregações/somas e o LLM apenas interpretar/formatar (`_buscar_contexto_agregado`) está correta e deve ser preservada — é o que evita alucinação numérica em respostas financeiras.
- A métrica de similaridade (`normalize_L2` + `IndexFlatIP` = cosseno) é consistente com o modelo de embedding usado.
- O pré-filtro SQL já usa parâmetros (`%s`), sem risco de SQL injection mesmo com entidades extraídas de texto livre via regex.
- O roteamento híbrido (agregação / semântico+filtro / semântico puro) está coberto por testes em `backend/tests/test_rag.py`.
