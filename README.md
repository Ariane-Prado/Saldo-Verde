# Saldo Verde

Sistema de gestão financeira agrícola com suporte a inteligência artificial para leitura de notas fiscais e consulta por linguagem natural.

Desenvolvido como projeto acadêmico na Universidade de Rio Verde.

---

## O que você precisa ter instalado

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — baixe, instale e abra antes de continuar
- [Git](https://git-scm.com/) — para baixar o projeto

---

## Como rodar o sistema

### 1. Baixe o projeto

Abra o terminal (Prompt de Comando ou PowerShell) e execute:

```bash
git clone https://github.com/Ariane-Prado/Saldo-Verde.git
cd Saldo-Verde
```

### 2. Suba o sistema com Docker

```bash
docker compose up --build
```

Aguarde até aparecer a mensagem que os 3 serviços estão rodando (banco, backend e frontend). Isso pode levar alguns minutos na primeira vez.

### 3. Acesse pelo navegador

Abra: **http://localhost:3000**

---

## Como fazer login

Na tela de login, clique no acesso disponível para preencher automaticamente, depois clique em **Entrar**.

| Usuário | Senha |
|---|---|
| `admin` | `admin123` |

Após o login, um tutorial interativo abre automaticamente mostrando todas as funcionalidades. Você pode pulá-lo e reabrir a qualquer momento pelo menu lateral.

---

## O que o sistema faz

### Cadastros — disponíveis sem configuração extra

| Tela | Para que serve |
|---|---|
| **Manter Pessoas** | Cadastrar fornecedores, clientes e faturados |
| **Manter Classificação** | Criar categorias de despesa e receita |
| **Manter Contas** | Registrar movimentações financeiras (A Pagar / A Receber) com parcelas |

Em todas as telas você pode buscar por texto, filtrar por tipo, ordenar as colunas clicando no cabeçalho e editar ou excluir registros.

Em **Manter Contas**, clique em qualquer linha da tabela para ver o detalhe completo da conta com todas as parcelas.

### Inteligência Artificial — requer chave Gemini

| Tela | Para que serve |
|---|---|
| **Nota Fiscal** | Envie um PDF e a IA extrai automaticamente os dados (fornecedor, valores, parcelas) |
| **Consulta IA** | Faça perguntas em linguagem natural sobre seus dados financeiros |

---

## Como configurar a chave de IA (Gemini)

A chave é gratuita e necessária apenas para as funcionalidades de IA.

1. Acesse [aistudio.google.com/apikey](https://aistudio.google.com/apikey) e gere uma chave
2. Defina a variável de ambiente `GEMINI_API_KEY` antes de subir o sistema

**Localmente (Docker):** adicione na seção `environment` do serviço backend no `docker-compose.yml`:

```yaml
environment:
  GEMINI_API_KEY: sua_chave_aqui
```

**Em produção (Render):** configure a variável `GEMINI_API_KEY` no painel de variáveis de ambiente do serviço.

---

## Como parar o sistema

No terminal onde o Docker está rodando, pressione `Ctrl + C`. Para remover tudo (incluindo os dados):

```bash
docker compose down -v
```

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + Vite |
| Backend | Python / Flask |
| Banco de dados | PostgreSQL 17 |
| IA | Google Gemini + FAISS |
| Infraestrutura | Docker + Docker Compose |

---

## Equipe

- Ariane Prado
- Rafael Paiva

Universidade de Rio Verde — Projeto N3, 2026
