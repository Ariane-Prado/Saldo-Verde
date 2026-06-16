import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "saldo_verde"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS PESSOAS (
                    id           SERIAL PRIMARY KEY,
                    tipo         VARCHAR(20) NOT NULL,
                    razao_social VARCHAR(255) NOT NULL,
                    cpf_cnpj     VARCHAR(20),
                    ativo        BOOLEAN NOT NULL DEFAULT TRUE
                );

                CREATE TABLE IF NOT EXISTS CLASSIFICACAO (
                    id        SERIAL PRIMARY KEY,
                    tipo      VARCHAR(20) NOT NULL,
                    descricao VARCHAR(255) NOT NULL,
                    ativo     BOOLEAN NOT NULL DEFAULT TRUE
                );

                CREATE TABLE IF NOT EXISTS MOVIMENTOCONTAS (
                    id                SERIAL PRIMARY KEY,
                    tipo              VARCHAR(20) NOT NULL DEFAULT 'APAGAR',
                    id_fornecedor     INTEGER REFERENCES PESSOAS(id),
                    id_faturado       INTEGER REFERENCES PESSOAS(id),
                    id_classificacao  INTEGER REFERENCES CLASSIFICACAO(id),
                    valor_total       NUMERIC(15,2),
                    data_emissao      DATE,
                    ativo             BOOLEAN NOT NULL DEFAULT TRUE
                );
                ALTER TABLE MOVIMENTOCONTAS ADD COLUMN IF NOT EXISTS descricao_itens TEXT;

                CREATE TABLE IF NOT EXISTS PARCELACONTAS (
                    id               SERIAL PRIMARY KEY,
                    id_movimento     INTEGER NOT NULL REFERENCES MOVIMENTOCONTAS(id),
                    identificacao    VARCHAR(50),
                    data_vencimento  DATE,
                    valor            NUMERIC(15,2),
                    ativo            BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)
        conn.commit()
