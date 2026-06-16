# Saldo Verde

Sistema de gestão financeira agrícola com suporte a inteligência artificial para leitura de notas fiscais e consulta por linguagem natural.

Desenvolvido como projeto acadêmico na Universidade de Rio Verde.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + Vite + CSS puro |
| Backend | Python 3 + Flask |
| Banco de dados | PostgreSQL 17 |
| IA / RAG | Google Gemini + FAISS |
| Infraestrutura | Docker + Docker Compose |

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução
- Git

---

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/Ariane-Prado/Saldo-Verde.git
cd Saldo-Verde
```

### 2. Escolha a branch mais completa

```bash
git checkout manual-usuario
```

> Esta branch contém todas as funcionalidades: CRUD, login, tutorial e ajustes de UX.

### 3. Suba os containers

```bash
docker compose up --build
```

O Docker irá:
- Criar e inicializar o banco de dados com schema e 200 registros de exemplo
- Subir a API Flask na porta **8000**
- Compilar e servir o frontend React via Nginx na porta **3000**

### 4. Acesse o sistema

Abra o navegador em: **http://localhost:3000**

---

## Credenciais de acesso

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `ariane` | `verde2025` | Ariane Prado |

> Clique em um dos acessos disponíveis na tela de login para preencher automaticamente.

---

## Funcionalidades

### Cadastros (sem necessidade de chave API)

| Módulo | Descrição |
|---|---|
| **Manter Pessoas** | Cadastro de Fornecedores, Clientes e Faturados com busca e filtro por tipo |
| **Manter Classificação** | Categorias de Despesa e Receita para organizar as movimentações |
| **Manter Contas** | Movimentações financeiras (A Pagar / A Receber) com suporte a múltiplas parcelas. Clique em uma linha para ver o detalhe completo da conta |

Todas as telas possuem:
- Busca por texto e filtro por tipo
- Botão **Todos** para listar todos os registros ativos
- Ordenação por coluna (clique no cabeçalho)
- Edição e exclusão lógica (soft-delete)

### Recursos de IA (requer chave Gemini)

| Módulo | Descrição |
|---|---|
| **Nota Fiscal** | Upload de PDF; a IA extrai automaticamente fornecedor, valores, parcelas e classificação |
| **Consulta IA** | Perguntas em linguagem natural sobre os dados financeiros via RAG Simples ou RAG com Embeddings |

---

## Configurar a chave Gemini

1. Acesse [aistudio.google.com/apikey](https://aistudio.google.com/apikey) e gere uma chave gratuita
2. No sistema, clique no botão de chave no rodapé da sidebar
3. Cole a chave e clique em **Salvar Chave**
4. O ícone ficará verde confirmando que está ativa

> A mesma chave serve tanto para o Upload de Nota Fiscal quanto para a Consulta IA.

---

## Tutorial integrado

O sistema possui um tutorial interativo que abre automaticamente após o login. Ele utiliza efeito *spotlight* para destacar cada elemento da interface com uma seta indicativa.

Para rever o tutorial a qualquer momento, clique em **Tutorial** no menu lateral (seção Ajuda).

---

## Estrutura de branches

| Branch | Conteúdo |
|---|---|
| `main` | Código base com funcionalidades RAG originais |
| `feature/banco` | Script SQL de seed com 200 registros + configuração Docker |
| `feature/backend` | Rotas CRUD da API Flask (Pessoas, Classificação, Contas) |
| `feature/frontend` | Componentes React CRUD (tabela, formulário modal, badges) |
| `feature/etapa4` | Integração: banco + backend + frontend |
| `feature/login` | Tela de login com credenciais placeholder |
| `manual-usuario` | Tutorial interativo, ajustes de UX e melhorias visuais |

---

## Estrutura do projeto

```
Saldo-Verde/
├── backend/              # API Flask
│   ├── app.py            # Rotas HTTP
│   ├── repository.py     # Acesso ao banco de dados
│   └── Dockerfile
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── App.jsx       # Layout principal + roteamento
│   │   ├── App.css       # Estilos globais
│   │   └── components/
│   │       ├── crud/     # ManterPessoas, ManterClassificacao, ManterContas
│   │       ├── Login.jsx
│   │       ├── Tutorial.jsx
│   │       ├── UploadNota.jsx
│   │       └── ConsultaRAG.jsx
│   └── Dockerfile
├── database/
│   ├── schema.sql        # Criação das tabelas
│   └── seed_200.sql      # 200 registros de exemplo
└── docker-compose.yml
```

---

## Parar o sistema

```bash
docker compose down
```

Para remover também os dados do banco:

```bash
docker compose down -v
```

---

## Equipe

- Ariane Prado
- Rafael Paiva
