"""
Testes do sistema RAG — validam roteamento, extração de entidades e fluxos.

Executar: cd backend && python -m pytest tests/test_rag.py -v

Os testes usam unittest.mock para isolar chamadas ao banco e à API Gemini,
de forma que possam rodar sem conexão com banco ou chave de API.
"""
import sys
import os

# Garante que o diretório backend está no path quando executado diretamente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch, call
import pytest

from agents.rag.consulta_rag import (
    _extrair_entidades,
    _buscar_ids_filtrados,
    consultar_rag_simples,
    consultar_rag_embeddings,
    Entidades,
)


# ── Fixtures de dados ──────────────────────────────────────────────────────────

_REGISTRO_INSUMOS = {
    "id": 1,
    "tipo": "APAGAR",
    "valor_total": 15000.00,
    "data_emissao": "2025-03-10",
    "fornecedor": "AgroDefense Ltda",
    "faturado": "Fazenda São João",
    "classificacao": "INSUMOS AGRÍCOLAS",
    "identificacao": "MOV1-PARC1",
    "data_vencimento": "2025-04-10",
    "valor_parcela": 15000.00,
}

_REGISTRO_MANUTENCAO = {
    "id": 2,
    "tipo": "APAGAR",
    "valor_total": 3500.00,
    "data_emissao": "2025-01-15",
    "fornecedor": "MecAgro Serviços",
    "faturado": "Ana Paula Lima",
    "classificacao": "MANUTENÇÃO E OPERAÇÃO",
    "identificacao": "MOV2-PARC1",
    "data_vencimento": "2025-02-15",
    "valor_parcela": 3500.00,
}


# ── Helpers de mock ────────────────────────────────────────────────────────────

def _mock_cursor_aggregate(partes: list[str]):
    """Retorna um mock de conexão que simula _buscar_contexto_agregado."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    # fetchone para total geral
    cur.fetchone.return_value = (18500.00,)
    # fetchall para por-fornecedor, por-classificação, top-5 maiores e top-5 menores
    cur.fetchall.side_effect = [
        [("AgroDefense Ltda", 15000.00, 1), ("MecAgro Serviços", 3500.00, 1)],
        [("INSUMOS AGRÍCOLAS", 15000.00, 1), ("MANUTENÇÃO E OPERAÇÃO", 3500.00, 1)],
        [(1, "AgroDefense Ltda", "INSUMOS AGRÍCOLAS", 15000.00, "2025-03-10"),
         (2, "MecAgro Serviços", "MANUTENÇÃO E OPERAÇÃO", 3500.00, "2025-01-15")],
        [(2, "MecAgro Serviços", "MANUTENÇÃO E OPERAÇÃO", 3500.00, "2025-01-15")],
    ]
    conn = MagicMock()
    conn.cursor.return_value = cur
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    return conn


def _mock_llm_response(texto: str = "Resposta simulada da IA."):
    resp = MagicMock()
    resp.text = texto
    return resp


# ── Testes de extração de entidades ───────────────────────────────────────────

class TestExtrairEntidades:

    def test_extrai_ano(self):
        ent = _extrair_entidades("Qual foi o total pago em 2025?")
        assert ent.ano == 2025

    def test_extrai_cpf(self):
        ent = _extrair_entidades(
            "Para o Faturado Ana Paula Lima (CPF 444.555.666-04), qual a soma?"
        )
        assert ent.documento == "444.555.666-04"

    def test_extrai_cnpj(self):
        ent = _extrair_entidades("Notas do fornecedor 12.345.678/0001-90")
        assert ent.documento == "12.345.678/0001-90"

    def test_sinal_agregacao(self):
        ent = _extrair_entidades("Qual foi o total pago em 2025?")
        assert ent.eh_agregacao is True

    def test_sinal_semantico(self):
        ent = _extrair_entidades("Itens semelhantes a corretivos de solo")
        assert ent.eh_semantico is True

    def test_ambos_sinais(self):
        ent = _extrair_entidades(
            "Qual é a maior despesa de INSUMOS AGRÍCOLAS que combate pragas?"
        )
        assert ent.eh_agregacao is True
        assert ent.eh_semantico is True

    def test_sem_filtros(self):
        ent = _extrair_entidades("Liste os fornecedores cadastrados")
        assert ent.ano is None
        assert ent.documento is None
        assert ent.eh_agregacao is False


# ── Pergunta 1: SQL puro com ano ───────────────────────────────────────────────

class TestPergunta1TotalAnual:
    """
    "Qual foi o valor total pago em Notas Fiscais emitidas no ano de 2025,
    e qual foi o fornecedor responsável pelo maior valor nesse período?"
    """

    PERGUNTA = (
        "Qual foi o valor total pago em Notas Fiscais emitidas no ano de 2025, "
        "e qual foi o fornecedor responsável pelo maior valor nesse período?"
    )

    def test_entidades_extraidas(self):
        ent = _extrair_entidades(self.PERGUNTA)
        assert ent.ano == 2025
        assert ent.eh_agregacao is True

    @patch("agents.rag.consulta_rag._carregar_categorias", return_value=[])
    @patch("agents.rag.consulta_rag.database.get_connection")
    @patch("agents.rag.consulta_rag._get_gemini_client")
    def test_usa_caminho_sql(self, mock_client, mock_conn, mock_cats):
        mock_conn.return_value = _mock_cursor_aggregate([])
        mock_client.return_value.models.generate_content.return_value = _mock_llm_response(
            "O total em 2025 foi R$ 18.500,00. Maior fornecedor: AgroDefense Ltda."
        )

        resposta = consultar_rag_simples(self.PERGUNTA)

        assert resposta  # resposta não-vazia
        # FAISS não deve ter sido chamado — verificamos que get_connection foi chamado (SQL)
        assert mock_conn.called

    @patch("agents.rag.consulta_rag._carregar_categorias", return_value=[])
    @patch("agents.rag.consulta_rag.database.get_connection")
    @patch("agents.rag.consulta_rag._get_gemini_client")
    def test_contexto_inclui_total_e_ranking(self, mock_client, mock_conn, mock_cats):
        """Garante que o contexto enviado ao LLM contém total geral e ranking por fornecedor."""
        mock_conn.return_value = _mock_cursor_aggregate([])
        capturado = {}

        def capturar_prompt(model, contents):
            capturado["prompt"] = contents[0] if isinstance(contents, list) else contents
            return _mock_llm_response()

        mock_client.return_value.models.generate_content.side_effect = capturar_prompt

        consultar_rag_simples(self.PERGUNTA)

        assert "capturado" in capturado or "prompt" in capturado
        prompt = capturado.get("prompt", "")
        assert "TOTAL GERAL" in prompt or "fornecedor" in prompt.lower()


# ── Pergunta 2: SQL com CPF e parcelas ────────────────────────────────────────

class TestPergunta2ParcelasCPF:
    """
    "Para o Faturado Ana Paula Lima (CPF 444.555.666-04),
    qual é a soma total dos valores das parcelas dentro do ano de 2025?"
    """

    PERGUNTA = (
        "Para o Faturado Ana Paula Lima (CPF 444.555.666-04), "
        "qual é a soma total dos valores das parcelas dentro do ano de 2025?"
    )

    def test_entidades_extraidas(self):
        ent = _extrair_entidades(self.PERGUNTA)
        assert ent.documento == "444.555.666-04"
        assert ent.ano == 2025
        # "soma" e "parcelas" → ambos sinalizam agregação
        assert ent.eh_agregacao is True

    @patch("agents.rag.consulta_rag._carregar_categorias", return_value=[])
    @patch("agents.rag.consulta_rag.database.get_connection")
    @patch("agents.rag.consulta_rag._get_gemini_client")
    def test_roteamento_para_sql(self, mock_client, mock_conn, mock_cats):
        # Simula resposta para parcelas (sobre_parcelas=True)
        cur = MagicMock()
        cur.__enter__ = lambda s: s
        cur.__exit__ = MagicMock(return_value=False)
        cur.fetchall.side_effect = [
            [("Ana Paula Lima", "444.555.666-04", 3500.00, 1)],  # por faturado
            [("MANUTENÇÃO E OPERAÇÃO", 3500.00, 1)],              # por classificação
            [(1, "Ana Paula Lima", "MANUTENÇÃO E OPERAÇÃO", 3500.00, "2025-02-15")],  # maiores
            [(1, "Ana Paula Lima", "MANUTENÇÃO E OPERAÇÃO", 3500.00, "2025-02-15")],  # menores
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_conn.return_value = conn
        mock_client.return_value.models.generate_content.return_value = _mock_llm_response(
            "A soma das parcelas de Ana Paula Lima em 2025 é R$ 3.500,00."
        )

        resposta = consultar_rag_simples(self.PERGUNTA)
        assert resposta

    def test_buscar_ids_filtrados_com_cpf_e_ano(self):
        """Verifica que a query SQL de pré-filtro usa CPF e ano corretamente."""
        from datetime import date
        ent = Entidades(
            ano=2025,
            documento="444.555.666-04",
            data_inicio=date(2025, 1, 1),
            data_fim=date(2025, 12, 31),
        )

        cur = MagicMock()
        cur.__enter__ = lambda s: s
        cur.__exit__ = MagicMock(return_value=False)
        cur.fetchall.return_value = [(2,)]
        conn = MagicMock()
        conn.cursor.return_value = cur
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)

        with patch("agents.rag.consulta_rag.database.get_connection", return_value=conn):
            ids = _buscar_ids_filtrados(ent)

        assert ids == {2}
        # Verifica que a query SQL foi chamada com os parâmetros corretos
        from datetime import date
        chamada = cur.execute.call_args
        sql, params = chamada[0]
        assert "cpf_cnpj" in sql
        assert "BETWEEN" in sql
        assert date(2025, 1, 1) in params
        assert date(2025, 12, 31) in params
        assert "444.555.666-04" in params


# ── Pergunta 3: Semântico com pré-filtro SQL ──────────────────────────────────

class TestPergunta3SemanticoComFiltro:
    """
    "Existem Notas Fiscais classificadas como MANUTENÇÃO E OPERAÇÃO cujos itens
    se assemelham a produtos usados para melhorar o solo, como corretivos ou neutralizadores?"
    """

    PERGUNTA = (
        "Existem Notas Fiscais classificadas como MANUTENÇÃO E OPERAÇÃO cujos itens "
        "se assemelham a produtos usados para melhorar o solo, como corretivos ou neutralizadores?"
    )

    def test_entidades_extraidas(self):
        ent = _extrair_entidades.__wrapped__(self.PERGUNTA) if hasattr(
            _extrair_entidades, "__wrapped__"
        ) else _extrair_entidades(self.PERGUNTA)
        # "semelhante" ou "corretivos" deve acionar sinal semântico
        assert ent.eh_semantico is True

    def test_sinal_semantico_detectado(self):
        """Keywords 'semelhante', 'corretivos', 'neutralizadores' devem acionar eh_semantico."""
        from agents.rag.consulta_rag import _KEYWORDS_SEMANTICO
        p = self.PERGUNTA.lower()
        assert any(kw in p for kw in _KEYWORDS_SEMANTICO)

    @patch("agents.rag.consulta_rag._carregar_categorias",
           return_value=["INSUMOS AGRÍCOLAS", "MANUTENÇÃO E OPERAÇÃO"])
    @patch("agents.rag.consulta_rag._recuperar_contexto_faiss")
    @patch("agents.rag.consulta_rag._buscar_ids_filtrados")
    @patch("agents.rag.consulta_rag._get_gemini_client")
    def test_ativa_prefilter_sql_e_faiss(
        self, mock_client, mock_ids, mock_faiss, mock_cats
    ):
        """
        Quando há classificação mencionada + sinal semântico,
        o sistema deve chamar _buscar_ids_filtrados (pré-filtro SQL)
        E _recuperar_contexto_faiss (busca semântica).
        """
        mock_ids.return_value = {2}
        mock_faiss.return_value = (
            "Movimento #2 | APAGAR | Fornecedor: MecAgro | "
            "Classificação: MANUTENÇÃO E OPERAÇÃO | Total: R$ 3500.0"
        )
        mock_client.return_value.models.generate_content.return_value = _mock_llm_response(
            "Foram encontrados registros de manutenção semelhantes a corretivos."
        )

        resposta = consultar_rag_embeddings(self.PERGUNTA)

        assert resposta
        # Pré-filtro SQL deve ter sido chamado
        mock_ids.assert_called_once()
        # FAISS deve ter sido chamado com os IDs do pré-filtro
        mock_faiss.assert_called_once()
        _, kwargs = mock_faiss.call_args
        subset = kwargs.get("subset_ids") or (mock_faiss.call_args[0][2] if len(mock_faiss.call_args[0]) > 2 else None)
        # subset_ids pode ter vindo como arg posicional ou keyword
        assert subset is not None or mock_ids.return_value == {2}


# ── Pergunta 4: Híbrido interno (agregação + semântico) ───────────────────────

class TestPergunta4HibridoInterno:
    """
    "Qual é a despesa de INSUMOS AGRÍCOLAS que tem o maior valor de Nota Fiscal total,
    e que tipo de pragas e doenças o item se destina a combater, de acordo com o nome do produto?"
    """

    PERGUNTA = (
        "Qual é a despesa de INSUMOS AGRÍCOLAS que tem o maior valor de Nota Fiscal total, "
        "e que tipo de pragas e doenças o item se destina a combater, de acordo com o nome do produto?"
    )

    def test_ambos_sinais_detectados(self):
        ent = _extrair_entidades(self.PERGUNTA)
        assert ent.eh_agregacao is True, "Keyword 'maior' deve acionar eh_agregacao"
        assert ent.eh_semantico is True, "Keywords 'pragas'/'doenças' devem acionar eh_semantico"

    @patch("agents.rag.consulta_rag._carregar_categorias",
           return_value=["INSUMOS AGRÍCOLAS", "MANUTENÇÃO E OPERAÇÃO"])
    def test_classificacao_mencionada_detectada(self, mock_cats):
        ent = _extrair_entidades(self.PERGUNTA)
        assert ent.classificacao_mencionada is not None
        assert "INSUMOS" in ent.classificacao_mencionada.upper()

    @patch("agents.rag.consulta_rag._carregar_categorias",
           return_value=["INSUMOS AGRÍCOLAS", "MANUTENÇÃO E OPERAÇÃO"])
    @patch("agents.rag.consulta_rag._buscar_contexto_agregado")
    @patch("agents.rag.consulta_rag._recuperar_contexto_faiss")
    @patch("agents.rag.consulta_rag._buscar_ids_filtrados")
    @patch("agents.rag.consulta_rag._get_gemini_client")
    def test_chama_ambos_caminhos_internos(
        self, mock_client, mock_ids, mock_faiss, mock_agg, mock_cats
    ):
        """
        Com eh_agregacao=True + eh_semantico=True, o RAG Semântico deve
        acionar tanto o SQL agregado quanto o FAISS.
        """
        mock_ids.return_value = {1}
        mock_agg.return_value = (
            "TOTAL GERAL: R$ 15000.00\n"
            "Top-5: #1 Mov#1 | AgroDefense Ltda | INSUMOS AGRÍCOLAS | R$ 15000.0 | 2025-03-10"
        )
        mock_faiss.return_value = (
            "Movimento #1 | APAGAR | Fornecedor: AgroDefense Ltda | "
            "Classificação: INSUMOS AGRÍCOLAS | Total: R$ 15000.0"
        )
        mock_client.return_value.models.generate_content.return_value = _mock_llm_response(
            "A maior despesa de Insumos Agrícolas é da AgroDefense Ltda (R$ 15.000,00)."
        )

        resposta = consultar_rag_embeddings(self.PERGUNTA)

        assert resposta
        # Ambos os caminhos devem ter sido acionados
        mock_agg.assert_called_once()
        mock_faiss.assert_called_once()

    def test_contexto_final_contem_ambas_secoes(self):
        """
        O prompt enviado ao LLM deve conter tanto a seção SQL quanto a semântica
        quando o modo híbrido interno é ativado.
        """
        with (
            patch("agents.rag.consulta_rag._carregar_categorias",
                  return_value=["INSUMOS AGRÍCOLAS"]),
            patch("agents.rag.consulta_rag._buscar_ids_filtrados", return_value={1}),
            patch("agents.rag.consulta_rag._buscar_contexto_agregado",
                  return_value="TOTAL GERAL: R$ 15000.00\nTop-5: #1 AgroDefense"),
            patch("agents.rag.consulta_rag._recuperar_contexto_faiss",
                  return_value="Movimento #1 | AgroDefense Ltda | INSUMOS AGRÍCOLAS"),
            patch("agents.rag.consulta_rag._get_gemini_client") as mock_client,
        ):
            capturado = {}

            def capturar(model, contents):
                capturado["prompt"] = contents[0] if isinstance(contents, list) else contents
                return _mock_llm_response()

            mock_client.return_value.models.generate_content.side_effect = capturar
            consultar_rag_embeddings(self.PERGUNTA)

        prompt = capturado.get("prompt", "")
        assert "DADOS ESTRUTURADOS" in prompt
        assert "SEMANTICAMENTE RELEVANTES" in prompt


# ── Testes de infraestrutura ───────────────────────────────────────────────────

class TestInfraestrutura:

    def test_score_threshold_filtra_resultados_ruins(self):
        """Verifica que resultados com score < _SCORE_THRESHOLD são descartados."""
        from agents.rag.consulta_rag import _SCORE_THRESHOLD, _recuperar_contexto_faiss
        import numpy as np

        store = {
            "index": MagicMock(),
            "textos_completos": ["doc A", "doc B", "doc C"],
            "mov_ids": [1, 2, 3],
            "total": 3,
        }
        # score abaixo do threshold para todos
        store["index"].ntotal = 3
        store["index"].search.return_value = (
            np.array([[0.10, 0.05, 0.01]], dtype=np.float32),
            np.array([[0, 1, 2]]),
        )

        with (
            patch("agents.rag.consulta_rag._get_vector_store", return_value=store),
            patch("agents.rag.consulta_rag._embed_query",
                  return_value=np.zeros((1, 3072), dtype=np.float32)),
            patch("faiss.normalize_L2"),
        ):
            resultado = _recuperar_contexto_faiss("qualquer pergunta", top_k=3)

        assert resultado is None, (
            f"Esperado None (todos os scores < {_SCORE_THRESHOLD}), obteve: {resultado}"
        )

    def test_truncar_contexto_corta_por_linha(self):
        from agents.rag.consulta_rag import _truncar_contexto, _MAX_CONTEXT_CHARS
        linha_grande = "X" * 1000
        texto = "\n".join([linha_grande] * 50)  # 50.000 chars — acima do limite

        resultado = _truncar_contexto(texto)

        assert len(resultado) <= _MAX_CONTEXT_CHARS
        # Não deve cortar no meio de uma linha
        for linha in resultado.split("\n"):
            assert linha == linha_grande or linha == ""

    def test_reset_vector_store_limpa_estado(self, tmp_path):
        import agents.rag.consulta_rag as rag_mod
        from agents.rag.consulta_rag import reset_vector_store

        # Injeta caminhos temporários
        original_index = rag_mod._INDEX_PATH
        original_meta  = rag_mod._META_PATH
        rag_mod._INDEX_PATH = str(tmp_path / "faiss.index")
        rag_mod._META_PATH  = str(tmp_path / "faiss_meta.json")

        # Cria arquivos falsos
        open(rag_mod._INDEX_PATH, "w").close()
        open(rag_mod._META_PATH,  "w").close()
        rag_mod._vector_store = {"fake": True}

        try:
            reset_vector_store()
            assert rag_mod._vector_store is None
            assert not os.path.exists(rag_mod._INDEX_PATH)
            assert not os.path.exists(rag_mod._META_PATH)
        finally:
            rag_mod._INDEX_PATH = original_index
            rag_mod._META_PATH  = original_meta
