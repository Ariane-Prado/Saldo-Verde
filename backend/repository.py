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


def buscar_movimento_por_nota(numero_nota_fiscal, cnpj_fornecedor):
    """Verifica se já existe um movimento ativo com a mesma nota fiscal e fornecedor."""
    if not numero_nota_fiscal or not cnpj_fornecedor:
        return None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT m.id FROM MOVIMENTOCONTAS m
                JOIN PESSOAS forn ON forn.id = m.id_fornecedor
                WHERE m.numero_nota_fiscal = %s AND forn.cpf_cnpj = %s AND m.ativo = TRUE
                """,
                (numero_nota_fiscal, cnpj_fornecedor)
            )
            row = cur.fetchone()
    return row[0] if row else None


def criar_movimento(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO MOVIMENTOCONTAS (tipo, id_fornecedor, id_faturado, id_classificacao, valor_total, data_emissao, descricao_itens, numero_nota_fiscal)
                VALUES ('APAGAR', %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    dados.get("id_fornecedor"),
                    dados.get("id_faturado"),
                    dados.get("id_classificacao"),
                    dados.get("valor_total"),
                    _normalizar_data(dados.get("data_emissao")),
                    dados.get("descricao_itens"),
                    dados.get("numero_nota_fiscal"),
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


# ─────────────────────────────────────────────────────────────
# CRUD — Pessoas
# ─────────────────────────────────────────────────────────────

def _rows_to_list(cur):
    colunas = [d[0] for d in cur.description]
    return [dict(zip(colunas, row)) for row in cur.fetchall()]


def _row_to_dict(cur, row):
    if row is None:
        return None
    colunas = [d[0] for d in cur.description]
    return dict(zip(colunas, row))


def listar_pessoas(q=None, tipo=None):
    params = []
    where = ["ativo = TRUE"]
    if q:
        where.append("(razao_social ILIKE %s OR cpf_cnpj ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    if tipo:
        where.append("tipo = %s")
        params.append(tipo)
    sql = f"SELECT id, tipo, razao_social, cpf_cnpj, ativo FROM PESSOAS WHERE {' AND '.join(where)} ORDER BY razao_social"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return _rows_to_list(cur)


def obter_pessoa(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, tipo, razao_social, cpf_cnpj, ativo FROM PESSOAS WHERE id = %s", (id,))
            return _row_to_dict(cur, cur.fetchone())


def inserir_pessoa(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO PESSOAS (tipo, razao_social, cpf_cnpj, ativo) VALUES (%s, %s, %s, TRUE) RETURNING id",
                (dados.get("tipo"), dados.get("razao_social"), dados.get("cpf_cnpj"))
            )
            novo_id = _fetch_id(cur, "PESSOAS")
        conn.commit()
    return novo_id


def atualizar_pessoa(id, dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE PESSOAS SET tipo=%s, razao_social=%s, cpf_cnpj=%s WHERE id=%s",
                (dados.get("tipo"), dados.get("razao_social"), dados.get("cpf_cnpj"), id)
            )
            atualizado = cur.rowcount > 0
        conn.commit()
    return atualizado


def desativar_pessoa(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE PESSOAS SET ativo=FALSE WHERE id=%s", (id,))
            atualizado = cur.rowcount > 0
        conn.commit()
    return atualizado


# ─────────────────────────────────────────────────────────────
# CRUD — Classificação
# ─────────────────────────────────────────────────────────────

def listar_classificacoes(q=None, tipo=None):
    params = []
    where = ["ativo = TRUE"]
    if q:
        where.append("descricao ILIKE %s")
        params.append(f"%{q}%")
    if tipo:
        where.append("tipo = %s")
        params.append(tipo)
    sql = f"SELECT id, tipo, descricao, ativo FROM CLASSIFICACAO WHERE {' AND '.join(where)} ORDER BY descricao"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return _rows_to_list(cur)


def obter_classificacao(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, tipo, descricao, ativo FROM CLASSIFICACAO WHERE id = %s", (id,))
            return _row_to_dict(cur, cur.fetchone())


def inserir_classificacao(dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO CLASSIFICACAO (tipo, descricao, ativo) VALUES (%s, %s, TRUE) RETURNING id",
                (dados.get("tipo"), dados.get("descricao"))
            )
            novo_id = _fetch_id(cur, "CLASSIFICACAO")
        conn.commit()
    return novo_id


def atualizar_classificacao(id, dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE CLASSIFICACAO SET tipo=%s, descricao=%s WHERE id=%s",
                (dados.get("tipo"), dados.get("descricao"), id)
            )
            atualizado = cur.rowcount > 0
        conn.commit()
    return atualizado


def desativar_classificacao(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE CLASSIFICACAO SET ativo=FALSE WHERE id=%s", (id,))
            atualizado = cur.rowcount > 0
        conn.commit()
    return atualizado


# ─────────────────────────────────────────────────────────────
# CRUD — MovimentoContas
# ─────────────────────────────────────────────────────────────

def listar_movimentos(q=None, tipo=None):
    params = []
    where = ["m.ativo = TRUE"]
    if q:
        where.append(
            "(pf.razao_social ILIKE %s OR pt.razao_social ILIKE %s "
            "OR c.descricao ILIKE %s OR CAST(m.valor_total AS TEXT) ILIKE %s)"
        )
        params += [f"%{q}%"] * 4
    if tipo:
        where.append("m.tipo = %s")
        params.append(tipo)
    sql = f"""
        SELECT m.id, m.tipo, m.valor_total, m.data_emissao, m.ativo,
               pf.razao_social AS fornecedor_nome,
               pt.razao_social AS faturado_nome,
               c.descricao     AS classificacao_descricao,
               m.id_fornecedor, m.id_faturado, m.id_classificacao,
               m.descricao_itens
        FROM MOVIMENTOCONTAS m
        LEFT JOIN PESSOAS pf ON m.id_fornecedor = pf.id
        LEFT JOIN PESSOAS pt ON m.id_faturado   = pt.id
        LEFT JOIN CLASSIFICACAO c ON m.id_classificacao = c.id
        WHERE {' AND '.join(where)}
        ORDER BY m.data_emissao DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = _rows_to_list(cur)
    for r in rows:
        if r.get("valor_total") is not None:
            r["valor_total"] = float(r["valor_total"])
        if r.get("data_emissao") is not None:
            r["data_emissao"] = r["data_emissao"].isoformat()
    return rows


def obter_movimento_completo(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT m.id, m.tipo, m.valor_total, m.data_emissao, m.ativo,
                       pf.razao_social AS fornecedor_nome,
                       pt.razao_social AS faturado_nome,
                       c.descricao     AS classificacao_descricao,
                       m.id_fornecedor, m.id_faturado, m.id_classificacao,
                       m.descricao_itens
                FROM MOVIMENTOCONTAS m
                LEFT JOIN PESSOAS pf ON m.id_fornecedor = pf.id
                LEFT JOIN PESSOAS pt ON m.id_faturado   = pt.id
                LEFT JOIN CLASSIFICACAO c ON m.id_classificacao = c.id
                WHERE m.id = %s
                """,
                (id,)
            )
            mov = _row_to_dict(cur, cur.fetchone())
        if mov is None:
            return None
        if mov.get("valor_total") is not None:
            mov["valor_total"] = float(mov["valor_total"])
        if mov.get("data_emissao") is not None:
            mov["data_emissao"] = mov["data_emissao"].isoformat()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, identificacao, data_vencimento, valor, ativo FROM PARCELACONTAS WHERE id_movimento=%s AND ativo=TRUE ORDER BY id",
                (id,)
            )
            parcelas = _rows_to_list(cur)
        for p in parcelas:
            if p.get("valor") is not None:
                p["valor"] = float(p["valor"])
            if p.get("data_vencimento") is not None:
                p["data_vencimento"] = p["data_vencimento"].isoformat()
        mov["parcelas"] = parcelas
    return mov


def inserir_movimento_crud(dados):
    parcelas = dados.get("parcelas", [])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO MOVIMENTOCONTAS
                    (tipo, id_fornecedor, id_faturado, id_classificacao, valor_total, data_emissao, descricao_itens)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    dados.get("tipo"),
                    dados.get("id_fornecedor"),
                    dados.get("id_faturado"),
                    dados.get("id_classificacao"),
                    dados.get("valor_total"),
                    _normalizar_data(dados.get("data_emissao")),
                    dados.get("descricao_itens"),
                )
            )
            id_mov = _fetch_id(cur, "MOVIMENTOCONTAS")
            for i, p in enumerate(parcelas, start=1):
                identificacao = p.get("identificacao") or f"MOV{id_mov}-PARC{i}"
                cur.execute(
                    "INSERT INTO PARCELACONTAS (id_movimento, identificacao, data_vencimento, valor) VALUES (%s, %s, %s, %s)",
                    (id_mov, identificacao, _normalizar_data(p.get("data_vencimento")), p.get("valor"))
                )
            if not parcelas:
                cur.execute(
                    "INSERT INTO PARCELACONTAS (id_movimento, identificacao, data_vencimento, valor) VALUES (%s, %s, %s, %s)",
                    (id_mov, f"MOV{id_mov}-PARC1", _normalizar_data(dados.get("data_emissao")), dados.get("valor_total"))
                )
        conn.commit()
    return id_mov


def atualizar_movimento_crud(id, dados):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE MOVIMENTOCONTAS
                SET tipo=%s, id_fornecedor=%s, id_faturado=%s,
                    id_classificacao=%s, valor_total=%s, data_emissao=%s,
                    descricao_itens=%s
                WHERE id=%s
                """,
                (
                    dados.get("tipo"),
                    dados.get("id_fornecedor"),
                    dados.get("id_faturado"),
                    dados.get("id_classificacao"),
                    dados.get("valor_total"),
                    _normalizar_data(dados.get("data_emissao")),
                    dados.get("descricao_itens"),
                    id,
                )
            )
            atualizado = cur.rowcount > 0
        conn.commit()
    return atualizado


def desativar_movimento(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE MOVIMENTOCONTAS SET ativo=FALSE WHERE id=%s", (id,))
            atualizado = cur.rowcount > 0
            cur.execute("UPDATE PARCELACONTAS SET ativo=FALSE WHERE id_movimento=%s", (id,))
        conn.commit()
    return atualizado


def obter_resumo_dashboard():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'ARECEBER' THEN valor_total ELSE 0 END)::NUMERIC, 0) AS receitas,
                    COALESCE(SUM(CASE WHEN tipo = 'APAGAR' THEN valor_total ELSE 0 END)::NUMERIC, 0) AS despesas,
                    COUNT(*) AS total_contas
                FROM MOVIMENTOCONTAS
                WHERE ativo = TRUE
            """)
            row = cur.fetchone()
            receitas = float(row[0]) if row else 0.0
            despesas = float(row[1]) if row else 0.0
            total_contas = int(row[2]) if row else 0
            saldo = receitas - despesas
            
            cur.execute("SELECT COUNT(*) FROM PESSOAS WHERE ativo = TRUE")
            total_pessoas = int(cur.fetchone()[0])
            
            cur.execute("SELECT COUNT(*) FROM CLASSIFICACAO WHERE ativo = TRUE")
            total_classificacoes = int(cur.fetchone()[0])

            return {
                "receitas": receitas,
                "despesas": despesas,
                "saldo": saldo,
                "total_contas": total_contas,
                "total_pessoas": total_pessoas,
                "total_classificacoes": total_classificacoes
            }

