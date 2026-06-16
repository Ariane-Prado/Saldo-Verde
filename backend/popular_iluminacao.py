"""
Script para popular o banco com 200 movimentos de iluminação para teste do FAISS.
Uso: python popular_iluminacao.py
Requer as variáveis de ambiente do banco configuradas (.env ou export).
"""
import random
from datetime import date, timedelta
from database import get_connection

FORNECEDORES = [
    ("LED TUBE SOLUCOES EM ILUMINACAO EIRELI", "12.345.678/0001-01"),
    ("PHILIPS LIGHTING BRASIL LTDA", "23.456.789/0001-02"),
    ("OSRAM DO BRASIL LTDA", "34.567.890/0001-03"),
    ("INTRAL INDUSTRIA DE MATERIAL ELETRICO", "45.678.901/0001-04"),
    ("BRONZEARTE ILUMINACAO LTDA", "56.789.012/0001-05"),
    ("LUMICENTER ILUMINACAO LTDA", "67.890.123/0001-06"),
    ("GE LIGHTING BRASIL", "78.901.234/0001-07"),
    ("SYLVANIA ILUMINACAO LTDA", "89.012.345/0001-08"),
    ("CREE LIGHTING DO BRASIL", "90.123.456/0001-09"),
    ("OPUS LUMINIS SOLUCOES EM LUZ", "01.234.567/0001-10"),
]

FATURADOS = [
    ("Lucas Junqueira Franco de Campos", "123.456.789-01"),
    ("Maria Fernanda Oliveira Silva", "234.567.890-02"),
    ("Carlos Eduardo Santos Lima", "345.678.901-03"),
    ("Ana Paula Rodrigues Costa", "456.789.012-04"),
    ("Pedro Henrique Alves Pereira", "567.890.123-05"),
]

ITENS = [
    "Lâmpada LED tubular T8 18W 6500K, calha de sobrepor LED 40W, fita LED 5050 RGB 5m",
    "Luminária industrial LED 100W, refletor LED 50W IP65, painel LED 36W embutir",
    "Poste LED 30W para área externa, projetor LED 20W bivolt, lâmpada bulbo LED 9W E27",
    "Luminária arandela LED 12W, spot LED embutir 7W, calha LED 2x20W para escritório",
    "Refletor LED 150W alto brilho, luminária de emergência LED, fita LED 2835 branco frio",
    "Lâmpada PAR30 LED 12W, downlight LED 15W embutir, luminária plafon LED 25W",
    "Luminária pendente LED 40W, trilho eletrificado + spots LED, painel slim LED 24W",
    "Cabo flexível PP 2x2,5mm para instalação elétrica de luminárias, disjuntor 20A",
    "Sensor de presença para iluminação automática, dimmer LED 300W, minuteria eletrônica",
    "Luminária fluorescente substituição LED T5 14W, starter eletrônico, reator eletrônico",
]

CLASSIFICACAO_ID = None
PESSOA_IDS = {}


def obter_ou_criar_classificacao(cur, descricao):
    cur.execute(
        "SELECT id FROM CLASSIFICACAO WHERE descricao = %s AND ativo = TRUE", (descricao,)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO CLASSIFICACAO (tipo, descricao) VALUES ('DESPESA', %s) RETURNING id",
        (descricao,),
    )
    return cur.fetchone()[0]


def obter_ou_criar_pessoa(cur, razao_social, cpf_cnpj, tipo):
    cur.execute(
        "SELECT id FROM PESSOAS WHERE cpf_cnpj = %s AND tipo = %s AND ativo = TRUE",
        (cpf_cnpj, tipo),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO PESSOAS (tipo, razao_social, cpf_cnpj) VALUES (%s, %s, %s) RETURNING id",
        (tipo, razao_social, cpf_cnpj),
    )
    return cur.fetchone()[0]


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            id_class = obter_ou_criar_classificacao(cur, "INFRAESTRUTURA E UTILIDADES")

            forn_ids = [
                obter_ou_criar_pessoa(cur, nome, cnpj, "FORNECEDOR")
                for nome, cnpj in FORNECEDORES
            ]
            fat_ids = [
                obter_ou_criar_pessoa(cur, nome, cpf, "FATURADO")
                for nome, cpf in FATURADOS
            ]

            inicio = date(2024, 1, 1)
            inseridos = 0
            for i in range(200):
                data_emissao = inicio + timedelta(days=random.randint(0, 540))
                valor = round(random.uniform(500, 15000), 2)
                itens = random.choice(ITENS)
                id_forn = random.choice(forn_ids)
                id_fat = random.choice(fat_ids)

                cur.execute(
                    """
                    INSERT INTO MOVIMENTOCONTAS
                        (tipo, id_fornecedor, id_faturado, id_classificacao,
                         valor_total, data_emissao, descricao_itens)
                    VALUES ('APAGAR', %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (id_forn, id_fat, id_class, valor, data_emissao, itens),
                )
                id_mov = cur.fetchone()[0]

                vencimento = data_emissao + timedelta(days=30)
                cur.execute(
                    """
                    INSERT INTO PARCELACONTAS (id_movimento, identificacao, data_vencimento, valor)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (id_mov, f"MOV{id_mov}-PARC1", vencimento, valor),
                )
                inseridos += 1

            conn.commit()
            print(f"✓ {inseridos} movimentos de iluminação inseridos com sucesso.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
