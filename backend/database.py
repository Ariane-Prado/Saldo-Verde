import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

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

                CREATE TABLE IF NOT EXISTS USUARIOS (
                    id          SERIAL PRIMARY KEY,
                    email       VARCHAR(255) NOT NULL UNIQUE,
                    senha_hash  VARCHAR(255) NOT NULL,
                    nome        VARCHAR(100) NOT NULL,
                    ativo       BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)

            # Insere usuário padrão se ainda não existir (credenciais via env vars)
            admin_email = os.getenv("ADMIN_EMAIL", "admin@saldoverde.com")
            admin_senha = os.getenv("ADMIN_SENHA", "admin123")
            cur.execute("""
                INSERT INTO USUARIOS (email, senha_hash, nome)
                VALUES (%s, %s, 'Administrador')
                ON CONFLICT (email) DO NOTHING
            """, (admin_email, generate_password_hash(admin_senha)))

        conn.commit()
