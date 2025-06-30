import csv
from collections import defaultdict

# Caminhos dos arquivos
arquivo_motor = 'relatorio_classificacao_itens.csv'  # Gerado pelo motor
arquivo_planilha = 'DADOS-COMPLETOS-ARTHUR-MARCO.csv'  # Ajuste se necessário

# Função para ler NCMs e valores do relatório do motor
def ler_motor(path):
    monofasicos = defaultdict(float)
    nao_monofasicos = defaultdict(float)
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncm = row['NCM'].strip().zfill(8)
            valor = float(row['Valor Total'])
            if row['Tipo'] == 'Monofasico':
                monofasicos[ncm] += valor
            else:
                nao_monofasicos[ncm] += valor
    return monofasicos, nao_monofasicos

# Função para ler NCMs e valores da planilha (ajuste conforme estrutura real)
def ler_planilha(path):
    monofasicos = defaultdict(float)
    nao_monofasicos = defaultdict(float)
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ncm = row.get('NCM', '').strip().zfill(8)
            valor = float(row.get('RB mono', '0').replace('$','').replace(',','').strip() or 0)
            if ncm:
                monofasicos[ncm] += valor
            valor_nao = float(row.get('RB não mono', '0').replace('$','').replace(',','').strip() or 0)
            if ncm:
                nao_monofasicos[ncm] += valor_nao
    return monofasicos, nao_monofasicos

# Leitura dos arquivos
a_motor, na_motor = ler_motor(arquivo_motor)
a_plan, na_plan = ler_planilha(arquivo_planilha)

# Comparação
def comparar_dicts(d1, d2, nome):
    print(f'\n--- Diferenças em {nome} ---')
    for ncm in sorted(set(d1) | set(d2)):
        v1 = d1.get(ncm, 0)
        v2 = d2.get(ncm, 0)
        if abs(v1 - v2) > 0.01:
            print(f'NCM: {ncm} | Motor: {v1:.2f} | Planilha: {v2:.2f} | Diferença: {v1-v2:.2f}')

comparar_dicts(a_motor, a_plan, 'Monofasicos')
comparar_dicts(na_motor, na_plan, 'Nao Monofasicos')
print('\nComparação concluída.')
