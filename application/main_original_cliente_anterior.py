import os
import json
from datetime import datetime
from parser import processar_xmls, carregar_pgdas, calcular_creditos, atualizar_selic
from core.domain.tabelas import consultar_selic, verificar_ncm_monofasico, calcular_selic_acumulada

def processar_periodo(periodo, diretorio_base):
    print(f"\n=== Processando período {periodo} ===\n")
    
    # Caminhos dos arquivos e diretórios
    dir_xmls = os.path.join(diretorio_base, "data/xmls", periodo)
    arquivo_pgdas = os.path.join(diretorio_base, "data/pgdas", f"{periodo}.json")
    
    # Verificar se diretório XML e arquivo PGDAS existem
    if not os.path.exists(dir_xmls):
        print(f"Erro: Diretório de XMLs não encontrado: {dir_xmls}")
        return None
    
    if not os.path.exists(arquivo_pgdas):
        print(f"Erro: Arquivo PGDAS não encontrado: {arquivo_pgdas}")
        return None
    
    # Carregar PGDAS
    print("Carregando dados do PGDAS...")
    dados_pgdas = carregar_pgdas(arquivo_pgdas)
    if not dados_pgdas:
        print("Erro ao carregar PGDAS")
        return None
    
    # Processar XMLs
    print("Processando XMLs de notas fiscais...")
    notas = processar_xmls(dir_xmls)
    if not notas:
        print("Nenhuma nota fiscal válida encontrada")
        return None
    
    # Calcular créditos
    print("Calculando créditos tributários...")
    resultados = calcular_creditos(notas, dados_pgdas)
    
    # Calcular fator SELIC acumulado desde o período até hoje
    fator_selic = calcular_selic_acumulada(periodo)
    print(f"Fator SELIC acumulado para {periodo} até hoje: {fator_selic:.4f}")
    
    # Atualizar créditos com SELIC acumulada
    resultados["creditos"]["atualizado"] = resultados["creditos"]["total"] * fator_selic
    resultados["fator_selic_acumulado"] = fator_selic
    
    # Salvar resultados
    diretorio_saida = os.path.join(diretorio_base, "data/resultados")
    os.makedirs(diretorio_saida, exist_ok=True)
    
    arquivo_saida = os.path.join(diretorio_saida, f"creditos_{periodo}.json")
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"Resultados salvos em: {arquivo_saida}")
    
    return resultados

def exibir_resultados(resultados, periodo):
    print("\n" + "="*50)
    print(f"RELATÓRIO DE CRÉDITOS TRIBUTÁRIOS - {periodo}")
    print("="*50 + "\n")
    
    # Estatísticas básicas
    print(f"Notas fiscais processadas: {resultados['estatisticas']['qtd_notas']}")
    print(f"Total de itens: {resultados['estatisticas']['qtd_itens_total']}")
    print(f"Itens monofásicos: {resultados['estatisticas']['qtd_itens_monofasicos']}")
    print(f"Itens não-monofásicos: {resultados['estatisticas']['qtd_itens_nao_monofasicos']}")
    
    # Valores
    print(f"\nTotal produtos monofásicos: R$ {resultados['total_monofasico']:.2f} ({resultados['proporcao_monofasico']:.2f}%)")
    print(f"Total produtos não-monofásicos: R$ {resultados['total_nao_monofasico']:.2f} ({100-resultados['proporcao_monofasico']:.2f}%)")
    
    # Alíquotas
    print(f"\nAlíquota efetiva: {resultados['aliquotas']['aliquota_efetiva']*100:.4f}%")
    print(f"Alíquota PIS: {resultados['aliquotas']['aliquota_pis']*100:.4f}%")
    print(f"Alíquota COFINS: {resultados['aliquotas']['aliquota_cofins']*100:.4f}%")
    
    # Tributos e créditos
    print("\nTRIBUTOS RECOLHIDOS:")
    print(f"PIS: R$ {resultados['tributos_recolhidos']['pis']:.2f}")
    print(f"COFINS: R$ {resultados['tributos_recolhidos']['cofins']:.2f}")
    
    print("\nTRIBUTOS DEVIDOS (sobre não-monofásicos):")
    print(f"PIS: R$ {resultados['tributos_devidos']['pis']:.2f}")
    print(f"COFINS: R$ {resultados['tributos_devidos']['cofins']:.2f}")
    
    print("\nCRÉDITOS TRIBUTÁRIOS:")
    print(f"Crédito PIS: R$ {resultados['creditos']['pis']:.2f}")
    print(f"Crédito COFINS: R$ {resultados['creditos']['cofins']:.2f}")
    print(f"Total: R$ {resultados['creditos']['total']:.2f}")
    print(f"Atualizado (Fator SELIC acumulado: {resultados['fator_selic_acumulado']:.4f}): R$ {resultados['creditos']['atualizado']:.2f}")

def main():
    # Diretório base do projeto
    diretorio_base = "/Users/trkia/Desktop/V12"
    
    # Período a processar (mês-ano)
    periodo = "2024-12"
    
    # Processar período
    resultados = processar_periodo(periodo, diretorio_base)
    
    # Exibir resultados
    if resultados:
        exibir_resultados(resultados, periodo)

if __name__ == "__main__":
    main()