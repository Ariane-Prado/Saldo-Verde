from database import get_connection
from datetime import datetime


def _normalizar_data(valor):
    """Converte DD/MM/YYYY para YYYY-MM-DD. Passa None sem alteracao."""
    if not valor:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valor).strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return valor  # retorna como está se não reconhecer o formato


def buscar_fornecedor(cnpj):
    if not cnpj:
        return {"existe": False}
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, razao_social, cpf_cnpj FROM PESSOAS WHERE cpf_cnpj = %s AND tipo = 'FORNECEDOR' AND ativo = TRUE",
                (cnpj,)
            )
            row = cur.fetchone()
    if row:
        return {"existe": True, "id": row[0], "dados": {"razao_social": row[1], "cpf_cnpj": row[2]}}
    return {"existe": False}


def buscar_faturado(cpf):
    if not cpf:
        return {"existe": False}
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, razao_social, cpf_cnpj FROM PESSOAS WHERE cpf_cnpj = %s AND tipo = 'FATURADO' AND ativo = TRUE",
                (cpf,)
            )
            row = cur.fetchone()
    if row:
        return {"existe": True, "id": row[0], "dados": {"razao_social": row[1], "cpf_cnpj": row[2]}}
    return {"existe": False}


def buscar_despesa(descricao):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM CLASSIFICACAO WHERE descricao ILIKE %s AND tipo = 'DESPESA' AND ativo = TRUE",
                (descricao,)
            )
            row = cur.fetchone()
    if row:
        return {"existe": True, "id": row[0]}
    return {"existe": False}


def _fetch_id(cur, contexto):
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"INSERT em {contexto} não retornou id")
    return row[0]


def criar_fornecedor(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO PESSOAS (tipo, razao_social, cpf_cnpj) VALUES ('FORNECEDOR', %s, %s) RETURNING id",
                (dados.get("razao_social"), dados.get("cnpj"))
            )
            novo_id = _fetch_id(cur, "PESSOAS/fornecedor")
        conn.commit()
    return novo_id


def criar_faturado(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO PESSOAS (tipo, razao_social, cpf_cnpj) VALUES ('FATURADO', %s, %s) RETURNING id",
                (dados.get("razao_social"), dados.get("cpf"))
            )
            novo_id = _fetch_id(cur, "PESSOAS/faturado")
        conn.commit()
    return novo_id


def criar_despesa(descricao):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO CLASSIFICACAO (tipo, descricao) VALUES ('DESPESA', %s) RETURNING id",
                (descricao,)
            )
            novo_id = _fetch_id(cur, "CLASSIFICACAO")
        conn.commit()
    return novo_id


def criar_movimento(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO MOVIMENTOCONTAS (tipo, id_fornecedor, id_faturado, id_classificacao, valor_total, data_emissao)
                VALUES ('APAGAR', %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    dados.get("id_fornecedor"),
                    dados.get("id_faturado"),
                    dados.get("id_classificacao"),
                    dados.get("valor_total"),
                    _normalizar_data(dados.get("data_emissao")),
                )
            )
            novo_id = _fetch_id(cur, "MOVIMENTOCONTAS")
        conn.commit()
    return novo_id


def criar_parcela(id_mov, dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO PARCELACONTAS (id_movimento, identificacao, data_vencimento, valor)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    id_mov,
                    dados.get("identificacao"),
                    _normalizar_data(dados.get("data_vencimento")),
                    dados.get("valor"),
                )
            )
            novo_id = _fetch_id(cur, "PARCELACONTAS")
        conn.commit()
    return novo_id
