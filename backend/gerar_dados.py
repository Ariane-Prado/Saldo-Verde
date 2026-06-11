import json
import random
from datetime import date, timedelta

random.seed(42)

fornecedores = [
    {"razao_social": "Agro Insumos Cerrado Ltda",     "cnpj": "11.222.333/0001-01"},
    {"razao_social": "PetroCampo Combustíveis S.A.",  "cnpj": "22.333.444/0001-02"},
    {"razao_social": "TerraVerde Maquinários Ltda",   "cnpj": "33.444.555/0001-03"},
    {"razao_social": "AgroFértil Nutrição Vegetal",   "cnpj": "44.555.666/0001-04"},
    {"razao_social": "Campo Forte Defensivos Ltda",   "cnpj": "55.666.777/0001-05"},
    {"razao_social": "SiloBrasil Armazenagem S.A.",   "cnpj": "66.777.888/0001-06"},
    {"razao_social": "MotoFarm Peças e Serviços",     "cnpj": "77.888.999/0001-07"},
    {"razao_social": "AgroTech Sementes Ltda",        "cnpj": "88.999.000/0001-08"},
    {"razao_social": "Irrigação Total S.A.",          "cnpj": "99.000.111/0001-09"},
    {"razao_social": "BioAgro Fertilizantes",         "cnpj": "10.111.222/0001-10"},
]

faturados = [
    {"razao_social": "João Carlos Silva",      "cpf": "111.222.333-01"},
    {"razao_social": "Maria Aparecida Santos", "cpf": "222.333.444-02"},
    {"razao_social": "Pedro Henrique Costa",   "cpf": "333.444.555-03"},
    {"razao_social": "Ana Paula Lima",         "cpf": "444.555.666-04"},
    {"razao_social": "Carlos Eduardo Rocha",   "cpf": "555.666.777-05"},
    {"razao_social": "Fazenda Boa Esperança",  "cpf": "666.777.888-06"},
    {"razao_social": "Sítio dos Ipês ME",      "cpf": "777.888.999-07"},
    {"razao_social": "Agropecuária Novo Mundo","cpf": "888.999.000-08"},
]

# Categorias com peso diferente para distribuição realista
categorias_config = [
    # (descricao, peso, faixa_valor_min, faixa_valor_max, descricao_detalhada)
    ("INSUMOS AGRÍCOLAS",       18, 800,   15000, "Fertilizantes, sementes e corretivos de solo"),
    ("COMBUSTÍVEL E LUBRIFICANTES", 15, 500, 8000,  "Diesel, gasolina, óleos e lubrificantes"),
    ("MANUTENÇÃO DE MÁQUINAS",  12, 600,  12000, "Conserto e revisão de tratores e colheitadeiras"),
    ("DEFENSIVOS AGRÍCOLAS",    10, 1200, 18000, "Herbicidas, fungicidas e inseticidas"),
    ("MÃO DE OBRA RURAL",       10, 1500,  6000, "Pagamento de diaristas e trabalhadores rurais"),
    ("AQUISIÇÃO DE EQUIPAMENTOS", 7, 5000, 80000, "Compra de tratores, implementos e equipamentos"),
    ("ARRENDAMENTO DE TERRA",    7, 3000, 25000, "Aluguel e arrendamento de áreas rurais"),
    ("SEMENTES E MUDAS",         6, 900,  10000, "Compra de sementes certificadas e mudas"),
    ("IRRIGAÇÃO",                5, 2000, 30000, "Bombeamento, tubulações e sistemas de irrigação"),
    ("ENERGIA ELÉTRICA RURAL",   4, 400,   3500, "Conta de energia e infraestrutura elétrica"),
    ("FRETE E LOGÍSTICA",        3, 800,   7000, "Transporte de grãos e insumos"),
    ("SEGURO RURAL",             3, 1500, 12000, "Seguro contra seca, geada e sinistros"),
]

# Expande pela proporção de peso
_pool = []
for cfg in categorias_config:
    _pool.extend([cfg] * cfg[1])


def gerar_data(ano_inicio=2024, ano_fim=2025):
    inicio = date(ano_inicio, 1, 1)
    fim    = date(ano_fim, 12, 31)
    delta  = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, delta))


def gerar_parcelas(valor_total, data_emissao, num_parcelas):
    parcelas = []
    valor_parc = round(valor_total / num_parcelas, 2)
    for i in range(1, num_parcelas + 1):
        venc = data_emissao + timedelta(days=30 * i)
        parcelas.append({
            "numero":          i,
            "data_vencimento": venc.isoformat(),
            "valor":           valor_parc,
        })
    # Ajusta centavos na última parcela
    soma = round(sum(p["valor"] for p in parcelas), 2)
    if soma != valor_total:
        parcelas[-1]["valor"] = round(parcelas[-1]["valor"] + (valor_total - soma), 2)
    return parcelas


registros = []
for i in range(200):
    cfg = random.choice(_pool)
    descricao, _, vmin, vmax, _ = cfg

    fornecedor  = random.choice(fornecedores)
    faturado    = random.choice(faturados)
    data_emissao = gerar_data()
    valor_total  = round(random.uniform(vmin, vmax), 2)

    # Parcelamento realista: valores altos → mais parcelas
    if valor_total > 20000:
        num_parc = random.choice([3, 4, 6, 12])
    elif valor_total > 5000:
        num_parc = random.choice([1, 2, 3])
    else:
        num_parc = 1

    parcelas = gerar_parcelas(valor_total, data_emissao, num_parc)

    registros.append({
        "fornecedor":  fornecedor,
        "faturado":    faturado,
        "despesa":     {"descricao": descricao},
        "valor_total": valor_total,
        "data_emissao": data_emissao.isoformat(),
        "parcelas":    parcelas,
    })

with open("dados.json", "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False, indent=2)

# Resumo
from collections import Counter
contagem = Counter(r["despesa"]["descricao"] for r in registros)
print("dados.json gerado com 200 registros\n")
print(f"{'Categoria':<35} {'Qtd':>5}  {'Total R$':>14}")
print("-" * 58)
for cat, qtd in sorted(contagem.items(), key=lambda x: -x[1]):
    total = sum(r["valor_total"] for r in registros if r["despesa"]["descricao"] == cat)
    print(f"{cat:<35} {qtd:>5}  R$ {total:>12,.2f}")
total_geral = sum(r["valor_total"] for r in registros)
print("-" * 58)
print(f"{'TOTAL':<35} {200:>5}  R$ {total_geral:>12,.2f}")
