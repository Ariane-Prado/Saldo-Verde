# Divisão de Tarefas — 2ª Etapa

**Entrega:** 14/05/2026 | **Peso:** 45% | **Disciplina:** Projeto Administrativo-Financeiro

A 1ª Etapa (extração de dados da NF via IA) já está implementada. A 2ª Etapa exige que, após a extração, o sistema consulte o banco de dados, informe o usuário sobre cada entidade (FORNECEDOR, FATURADO, DESPESA), crie os registros ausentes e registre o movimento financeiro (MOVIMENTOCONTAS + PARCELACONTAS).

A divisão abaixo separa os desenvolvedores por **camada da aplicação** para eliminar conflitos de merge.

---

## Desenvolvedor 1 — Backend + Banco de Dados

> Camada: `backend/` e `database/`

### 1. Criar o schema PostgreSQL
- **Arquivo:** `database/schema.sql`
- Criar as tabelas seguindo o DER existente (`DER.pdf` / `DER.png`):

| Tabela | Campos principais |
|---|---|
| `PESSOAS` | id, tipo (CLIENTE-FORNECEDOR \| FATURADO), razao_social, cpf_cnpj, ativo |
| `CLASSIFICACAO` | id, tipo (DESPESA \| RECEITA), descricao, ativo |
| `MOVIMENTOCONTAS` | id, tipo (APAGAR \| ARECEBER), id_fornecedor, id_faturado, valor_total, data_emissao, ativo |
| `PARCELACONTAS` | id, id_movimento, identificacao (UNIQUE), data_vencimento, valor, ativo |

### 2. Configurar conexão com PostgreSQL
- **Arquivo novo:** `backend/database.py`
- Usar `psycopg2` (já está no `requirements.txt`)
- Ler credenciais do `.env`

### 3. Camada de repositório
- **Arquivo novo:** `backend/repository.py`

| Função | Descrição |
|---|---|
| `buscar_fornecedor(cnpj)` | Retorna `{existe, id, dados}` ou `None` |
| `buscar_faturado(cpf)` | Retorna `{existe, id, dados}` ou `None` |
| `buscar_despesa(descricao)` | Retorna `{existe, id}` ou `None` |
| `criar_fornecedor(dados)` | Insere em PESSOAS tipo CLIENTE-FORNECEDOR, retorna id |
| `criar_faturado(dados)` | Insere em PESSOAS tipo FATURADO, retorna id |
| `criar_despesa(descricao)` | Insere em CLASSIFICACAO tipo DESPESA, retorna id |
| `criar_movimento(dados)` | Insere em MOVIMENTOCONTAS, retorna id |
| `criar_parcela(id_mov, dados)` | Insere em PARCELACONTAS |

### 4. Nova rota `POST /analisar`
- **Arquivo modificado:** `backend/app.py` (apenas **adiciona** a rota, sem tocar na `/extrair`)
- Recebe JSON com dados extraídos da nota, chama `repository.py` e retorna:

```json
{
  "fornecedor": { "existe": false, "id_criado": 5 },
  "faturado":   { "existe": true,  "id": 19 },
  "despesa":    { "existe": true,  "id": 22 },
  "movimento_id": 10,
  "parcela_id":   14,
  "sucesso": true
}
```

---

## Desenvolvedor 2 — Frontend + Integração

> Camada: `frontend/`

### 1. Componente `ResultadoAnalise`
- **Arquivo novo:** `frontend/src/components/ResultadoAnalise.jsx`
- Exibir resultado no formato exigido pelo professor:

```
FORNECEDOR:
IGUAÇU MAQUINAS LTDA
CNPJ: 11.111.111/0001-00
NÃO EXISTE          ← vermelho

FATURADO
BELTRANO DA SILVA
CPF: 999.999.999-99
EXISTE – ID: 19     ← verde

DESPESA
MANUTENÇÃO E OPERAÇÃO
EXISTE – ID: 22     ← verde
```

### 2. Adaptar `UploadNota`
- **Arquivo modificado:** `frontend/src/components/UploadNota.jsx`
- Após receber o JSON da extração, fazer 2ª chamada `POST /analisar`
- Exibir loading durante a chamada
- Renderizar `ResultadoAnalise` com a resposta recebida

### 3. Mensagem de sucesso final
- Após o ciclo completo, exibir:  
  > _"Registro lançado com sucesso! Movimento #ID criado."_
- Implementar em `UploadNota.jsx` ou como componente `Sucesso.jsx`

### 4. Estilos
- **Arquivo modificado:** `frontend/src/App.css`
- Vermelho para **NÃO EXISTE**, verde para **EXISTE – ID: X**
- Separação visual clara entre as seções FORNECEDOR / FATURADO / DESPESA

---

## Contrato de API (trabalho paralelo sem bloqueio)

Dev 2 pode **mockar** a resposta do `/analisar` localmente enquanto Dev 1 implementa o endpoint real.

**Body enviado ao `POST /analisar`:**

```json
{
  "fornecedor": { "razao_social": "...", "cnpj": "..." },
  "faturado":   { "razao_social": "...", "cpf":  "..." },
  "despesa":    { "descricao": "..." },
  "valor_total": 0.00,
  "data_emissao": "YYYY-MM-DD"
}
```

---

## Arquivos por desenvolvedor (sem sobreposição)

| Desenvolvedor | Arquivos |
|---|---|
| Dev 1 (Backend) | `database/schema.sql` |
| Dev 1 (Backend) | `backend/database.py` _(novo)_ |
| Dev 1 (Backend) | `backend/repository.py` _(novo)_ |
| Dev 1 (Backend) | `backend/app.py` — só adiciona rota `/analisar` |
| Dev 2 (Frontend) | `frontend/src/components/ResultadoAnalise.jsx` _(novo)_ |
| Dev 2 (Frontend) | `frontend/src/components/UploadNota.jsx` |
| Dev 2 (Frontend) | `frontend/src/App.css` |

> **Obs.:** O único arquivo compartilhado é `backend/app.py`. Dev 1 apenas **adiciona** a rota `/analisar` sem tocar na `/extrair` existente — risco de conflito mínimo.

---

## Docker (entrega final — ambos colaboram)

- `Dockerfile` para o backend (Python/Flask)
- `Dockerfile` para o frontend (Node/Vite)
- `docker-compose.yml` na raiz com 3 serviços: **frontend**, **backend**, **postgres**
- Pode ser feito por qualquer um após as camadas estarem prontas

---

## Verificação / Como testar

1. Subir PostgreSQL e rodar `database/schema.sql`
2. Subir backend (`python app.py`) e frontend (`npm run dev`)
3. Fazer upload de um PDF de nota fiscal
4. Verificar que a tela exibe o status de FORNECEDOR, FATURADO e DESPESA corretamente
5. Verificar no banco que os registros foram inseridos
6. Verificar mensagem de sucesso no frontend
