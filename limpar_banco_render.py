import psycopg2
import sys

def limpar_banco():
    print("=== Saldo Verde — Utilitário de Limpeza de Banco (Render) ===")
    print("Este script irá esvaziar as tabelas transacionais no Render, mantendo intactos os usuários administradores.\n")

    # Solicita a URL Externa do Render
    url_render = input("Cole a sua 'External Database URL' do Render (ex: postgresql://...): ").strip()

    if not url_render:
        print("Erro: A URL do banco de dados não pode ser vazia.")
        sys.exit(1)

    if not url_render.startswith("postgres://") and not url_render.startswith("postgresql://"):
        print("Erro: A URL deve iniciar com 'postgresql://' ou 'postgres://'.")
        sys.exit(1)

    # Confirmação de segurança
    confirmacao = input("\nTem certeza absoluta de que deseja limpar o banco de dados no Render? (digite 'sim' para confirmar): ").strip().lower()
    if confirmacao != 'sim':
        print("Operação cancelada pelo usuário.")
        sys.exit(0)

    try:
        print("\nConectando ao banco de dados no Render...")
        # Conecta no PostgreSQL do Render usando a string de conexão
        conn = psycopg2.connect(url_render)
        
        with conn.cursor() as cur:
            print("Executando a limpeza das tabelas (Truncate)...")
            cur.execute("""
                TRUNCATE TABLE 
                    PARCELACONTAS, 
                    MOVIMENTOCONTAS, 
                    PESSOAS, 
                    CLASSIFICACAO 
                RESTART IDENTITY CASCADE;
            """)
            conn.commit()
            print("Sucesso! Tabelas limpas e contadores de ID zerados.")
            
    except psycopg2.Error as e:
        print(f"\nErro do banco de dados: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Conexão fechada.")

if __name__ == "__main__":
    limpar_banco()
