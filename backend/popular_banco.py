import json
import sys
import repository

arquivo = sys.argv[1] if len(sys.argv) > 1 else "dados.json"

with open(arquivo, "r", encoding="utf-8") as f:
    registros = json.load(f)

total = len(registros)
ok = 0
erros = 0

for i, item in enumerate(registros):
    try:
        fornecedor_input = item.get("fornecedor", {})
        faturado_input   = item.get("faturado", {})
        despesa_input    = item.get("despesa", {})
        valor_total      = item.get("valor_total", 0)
        data_emissao     = item.get("data_emissao")
        parcelas         = item.get("parcelas", [])

        res_forn = repository.buscar_fornecedor(fornecedor_input.get("cnpj"))
        id_fornecedor = res_forn["id"] if res_forn["existe"] else repository.criar_fornecedor(fornecedor_input)

        res_fat = repository.buscar_faturado(faturado_input.get("cpf"))
        id_faturado = res_fat["id"] if res_fat["existe"] else repository.criar_faturado(faturado_input)

        res_desp = repository.buscar_despesa(despesa_input.get("descricao", ""))
        id_classificacao = res_desp["id"] if res_desp["existe"] else repository.criar_despesa(despesa_input.get("descricao", ""))

        id_movimento = repository.criar_movimento({
            "id_fornecedor":    id_fornecedor,
            "id_faturado":      id_faturado,
            "id_classificacao": id_classificacao,
            "valor_total":      valor_total,
            "data_emissao":     data_emissao,
        })

        if parcelas:
            for p in parcelas:
                repository.criar_parcela(id_movimento, {
                    "identificacao":   f"MOV{id_movimento}-PARC{p.get('numero', 1)}",
                    "data_vencimento": p.get("data_vencimento") or data_emissao,
                    "valor":           p.get("valor", valor_total),
                })
        else:
            repository.criar_parcela(id_movimento, {
                "identificacao":   f"MOV{id_movimento}-PARC1",
                "data_vencimento": data_emissao,
                "valor":           valor_total,
            })

        ok += 1
        print(f"[{i+1}/{total}] OK — movimento #{id_movimento}")

    except Exception as e:
        erros += 1
        print(f"[{i+1}/{total}] ERRO — {e}")

print(f"\nConcluído: {ok} inseridos, {erros} erros.")
