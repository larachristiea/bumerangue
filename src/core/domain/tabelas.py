import os
import json
from datetime import datetime

# Diretório das tabelas
DIR_TABELAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tabelas")

# Mapas de meses
MESES = {
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março', 
    '04': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}

# Função para carregar uma tabela JSON
def carregar_tabela(nome_arquivo):
    caminho = os.path.join(DIR_TABELAS, nome_arquivo)
    try:
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Erro ao carregar tabela {nome_arquivo}: {str(e)}")
        return None

# Função para consultar taxa SELIC
def consultar_selic(periodo):
    """
    Consulta a taxa SELIC para o período especificado.
    
    Args:
        periodo: string no formato "YYYY-MM" ou "MM/YYYY"
    
    Returns:
        float: Taxa SELIC mensal para o período, ou None se não encontrada
    """
    # Normalizar formato do período para extrair mês e ano
    if '-' in periodo:
        ano, mes = periodo.split('-')
    elif '/' in periodo:
        mes, ano = periodo.split('/')
    else:
        return None
    
    # Ajustar para o formato da tabela
    nome_mes = MESES.get(mes)
    if not nome_mes:
        return None
    
    # Carregar tabela SELIC
    tabela_selic = carregar_tabela("Tabela Selic.json")
    if not tabela_selic:
        return None
    
    # Buscar taxa SELIC para o mês e ano
    for linha in tabela_selic:
        if linha.get("Mês/Ano") == nome_mes:
            taxa = linha.get(ano)
            if taxa is not None:
                return float(taxa)
    
    return None

def calcular_selic_acumulada(periodo_inicial, periodo_final=None):
    """
    Calcula a taxa SELIC acumulada entre dois períodos.
    
    Args:
        periodo_inicial: string no formato "YYYY-MM" (período da apuração)
        periodo_final: string no formato "YYYY-MM" (período até onde acumular, padrão: hoje)
    
    Returns:
        float: Fator SELIC acumulado (1 + taxa acumulada)
    """
    # Se período final não for fornecido, usar mês/ano atual
    if periodo_final is None:
        data_atual = datetime.now()
        periodo_final = f"{data_atual.year}-{data_atual.month:02d}"
    
    # Normalizar formatos
    if '-' in periodo_inicial:
        ano_inicial, mes_inicial = periodo_inicial.split('-')
    elif '/' in periodo_inicial:
        mes_inicial, ano_inicial = periodo_inicial.split('/')
    else:
        return 1.0  # Retornar 1.0 (sem atualização) em caso de erro
    
    if '-' in periodo_final:
        ano_final, mes_final = periodo_final.split('-')
    elif '/' in periodo_final:
        mes_final, ano_final = periodo_final.split('/')
    else:
        return 1.0  # Retornar 1.0 (sem atualização) em caso de erro
    
    # Converter para inteiros
    ano_inicial = int(ano_inicial)
    mes_inicial = int(mes_inicial)
    ano_final = int(ano_final)
    mes_final = int(mes_final)
    
    # Carregar tabela SELIC
    tabela_selic = carregar_tabela("Tabela Selic.json")
    if not tabela_selic:
        return 1.0
    
    # Criar mapeamento de meses/anos para taxas
    mapa_selic = {}
    for linha in tabela_selic:
        mes_nome = linha.get("Mês/Ano")
        if mes_nome not in MESES.values():
            continue
        
        # Obter número do mês
        mes_num = None
        for num, nome in MESES.items():
            if nome == mes_nome:
                mes_num = int(num)
                break
        
        if mes_num is None:
            continue
        
        for ano_col in linha.keys():
            if ano_col == "Mês/Ano":
                continue
            
            try:
                ano_num = int(ano_col)
                taxa = linha.get(ano_col)
                if taxa is not None:
                    mapa_selic[(ano_num, mes_num)] = float(taxa)
            except (ValueError, TypeError):
                continue
    
    # Calcular SELIC acumulada
    fator_acumulado = 1.0
    
    # Iniciar a partir do mês seguinte ao período inicial
    ano_atual = ano_inicial
    mes_atual = mes_inicial + 1
    if mes_atual > 12:
        mes_atual = 1
        ano_atual += 1
    
    # Acumular até o mês do período final
    while (ano_atual < ano_final) or (ano_atual == ano_final and mes_atual <= mes_final):
        taxa = mapa_selic.get((ano_atual, mes_atual), 0)
        fator_acumulado *= (1 + taxa)
        
        # Avançar para o próximo mês
        mes_atual += 1
        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1
    
    return fator_acumulado

# Função para verificar se um NCM é monofásico
def verificar_ncm_monofasico(ncm):
    """
    Verifica se um NCM está na lista de NCMs monofásicos.
    
    Args:
        ncm: string com o código NCM (8 dígitos)
    
    Returns:
        bool: True se o NCM for monofásico, False caso contrário
    """
    # Converter para inteiro para facilitar a comparação
    try:
        ncm_int = int(ncm)
    except (ValueError, TypeError):
        return False
    
    # Carregar tabela de NCMs monofásicos
    tabela_ncm = carregar_tabela("Espelho de ncms monofásicas.json")
    if not tabela_ncm:
        return False
    
    # Verificar se o NCM está na lista
    for item in tabela_ncm:
        if item.get("NCMs monofásicos") == ncm_int:
            return True
    
    return False

# Função para obter alíquota e valor a deduzir do Simples Nacional
def obter_parametros_simples(receita_bruta, anexo=1):
    """
    Obtém a alíquota nominal e o valor a deduzir do Simples Nacional.
    
    Args:
        receita_bruta: float com a receita bruta em 12 meses
        anexo: int com o número do anexo (1 a 5)
    
    Returns:
        tuple: (alíquota nominal, valor a deduzir) ou (None, None) se não encontrado
    """
    # Para o MVP, definir manualmente os valores da tabela
    # Com base na tabela do Simples Nacional para 2024
    faixas = [
        {"limite_inferior": 0, "limite_superior": 180000, "aliquota": 0.04, "valor_deduzir": 0},
        {"limite_inferior": 180000.01, "limite_superior": 360000, "aliquota": 0.073, "valor_deduzir": 5940},
        {"limite_inferior": 360000.01, "limite_superior": 720000, "aliquota": 0.095, "valor_deduzir": 13860},
        {"limite_inferior": 720000.01, "limite_superior": 1800000, "aliquota": 0.107, "valor_deduzir": 22500},
        {"limite_inferior": 1800000.01, "limite_superior": 3600000, "aliquota": 0.143, "valor_deduzir": 87300},
        {"limite_inferior": 3600000.01, "limite_superior": 4800000, "aliquota": 0.19, "valor_deduzir": 378000}
    ]
    
    # Encontrar a faixa correspondente à receita bruta
    for faixa in faixas:
        if faixa["limite_inferior"] <= receita_bruta <= faixa["limite_superior"]:
            return faixa["aliquota"], faixa["valor_deduzir"]
    
    return None, None

# Função para calcular alíquota efetiva
def calcular_aliquota_efetiva(receita_bruta, aliquota_nominal, valor_deduzir):
    """
    Calcula a alíquota efetiva do Simples Nacional.
    
    Args:
        receita_bruta: float com a receita bruta em 12 meses
        aliquota_nominal: float com a alíquota nominal
        valor_deduzir: float com o valor a deduzir
    
    Returns:
        float: Alíquota efetiva
    """
    return (receita_bruta * aliquota_nominal - valor_deduzir) / receita_bruta

# Teste das funções
if __name__ == "__main__":
    # Testar consulta de SELIC
    periodo_teste = "2024-12"
    taxa_selic = consultar_selic(periodo_teste)
    print(f"Taxa SELIC para {periodo_teste}: {taxa_selic}")
    
    # Testar verificação de NCM monofásico
    ncm_teste = "30049069"
    eh_monofasico = verificar_ncm_monofasico(ncm_teste)
    print(f"NCM {ncm_teste} é monofásico? {eh_monofasico}")
    
    # Testar parâmetros do Simples
    receita_teste = 1343467.76
    aliquota, valor_deduzir = obter_parametros_simples(receita_teste)
    print(f"Alíquota nominal: {aliquota}, Valor a deduzir: {valor_deduzir}")
    
    # Testar cálculo de alíquota efetiva
    if aliquota is not None and valor_deduzir is not None:
        aliquota_efetiva = calcular_aliquota_efetiva(receita_teste, aliquota, valor_deduzir)
        print(f"Alíquota efetiva: {aliquota_efetiva:.6f}")