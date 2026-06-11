-- =============================================
-- Saldo Verde — Schema do Banco de Dados
-- =============================================

-- PESSOAS: Armazena fornecedores (CLIENTE-FORNECEDOR) e faturados (FATURADO)
CREATE TABLE IF NOT EXISTS PESSOAS (
    id           SERIAL PRIMARY KEY,
    tipo         VARCHAR(20) NOT NULL CHECK (tipo IN ('FORNECEDOR', 'CLIENTE', 'FATURADO')),
    razao_social VARCHAR(200) NOT NULL,
    cpf_cnpj     VARCHAR(20),
    ativo        BOOLEAN NOT NULL DEFAULT TRUE
);

-- CLASSIFICACAO: Armazena tipos de despesa e receita
CREATE TABLE IF NOT EXISTS CLASSIFICACAO (
    id        SERIAL PRIMARY KEY,
    tipo      VARCHAR(10) NOT NULL CHECK (tipo IN ('DESPESA', 'RECEITA')),
    descricao VARCHAR(200) NOT NULL,
    ativo     BOOLEAN NOT NULL DEFAULT TRUE
);

-- MOVIMENTOCONTAS: Registros de contas a pagar / a receber
CREATE TABLE IF NOT EXISTS MOVIMENTOCONTAS (
    id               SERIAL PRIMARY KEY,
    tipo             VARCHAR(10) NOT NULL CHECK (tipo IN ('APAGAR', 'ARECEBER')),
    id_fornecedor    INT REFERENCES PESSOAS(id),
    id_faturado      INT REFERENCES PESSOAS(id),
    id_classificacao INT REFERENCES CLASSIFICACAO(id),
    valor_total      DECIMAL(15, 2) NOT NULL,
    data_emissao     DATE,
    ativo            BOOLEAN NOT NULL DEFAULT TRUE
);

-- PARCELACONTAS: Parcelas de cada movimento
CREATE TABLE IF NOT EXISTS PARCELACONTAS (
    id              SERIAL PRIMARY KEY,
    id_movimento    INT NOT NULL REFERENCES MOVIMENTOCONTAS(id),
    identificacao   VARCHAR(100) NOT NULL UNIQUE,
    data_vencimento DATE,
    valor           DECIMAL(15, 2) NOT NULL,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE
);
