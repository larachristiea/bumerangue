import os
import json
import xml.etree.ElementTree as ET

# Diretórios e arquivos - CORRIGIDO PARA 2022
DIR_XMLS = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/xmls/2022-12"
ESPELHO_NCM_MONOFASICA = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/tabelas/Espelho de ncms monofásicas.json"
PGDAS_FILE = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/pgdas/2022-12.json"  # Será simulado
ANEXO_SIMPLES_FILE = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/tabelas/Anexo do Simples.json"

def carregar_espelho_ncm_monofasica():
    """
    Carrega a lista de NCMs monofásicos do arquivo espelho JSON.
    Retorna um set com os NCMs para busca rápida.
    """
    try:
        with open(ESPELHO_NCM_MONOFASICA, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
            ncms_monofasicos = set()
            for item in dados:
                if item and "NCMs monofásicos" in item:
                    ncm = str(item["NCMs monofásicos"])
                    ncms_monofasicos.add(ncm)
            return ncms_monofasicos
    except FileNotFoundError:
        print(f"⚠️ ERRO: Arquivo {ESPELHO_NCM_MONOFASICA} não encontrado!")
        return set()
    except Exception as e:
        print(f"⚠️ ERRO ao carregar espelho de NCM: {str(e)}")
        return set()

def carregar_dados_pgdas():
    """
    Carrega os dados do PGDAS para o período.
    """
    try:
        with open(PGDAS_FILE, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except Exception as e:
        print(f"⚠️ ERRO ao carregar PGDAS: {str(e)}")
        return None

def carregar_anexo_simples():
    """
    Carrega a tabela do Anexo do Simples Nacional.
    """
    try:
        with open(ANEXO_SIMPLES_FILE, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except Exception as e:
        print(f"⚠️ ERRO ao carregar Anexo do Simples: {str(e)}")
        return None

def identificar_faixa_tributacao(rbt12, anexo_simples_data):
    """
    Identifica a faixa de tributação baseada na RBT12.
    Retorna a alíquota nominal e valor dedução da faixa correspondente.
    """
    if not anexo_simples_data or "anexo_1" not in anexo_simples_data:
        print("⚠️ ERRO: Dados do Anexo I não encontrados")
        return None, None, None
    
    faixas = anexo_simples_data["anexo_1"]
    
    for faixa in faixas:
        limite_inicial = faixa.get("receita_bruta_anual_minima", 0)
        limite_final = faixa.get("receita_bruta_anual_maxima", float('inf'))
        
        if limite_inicial <= rbt12 <= limite_final:
            faixa_numero = faixa.get("faixa", "N/A")
            aliquota_nominal = faixa.get("aliquota", 0) / 100  # Converte para decimal
            valor_deducao = faixa.get("valor_a_deduzir", 0)
            
            print(f"🎯 Faixa identificada: {faixa_numero}")
            print(f"   RBT12: R$ {rbt12:,.2f}")
            print(f"   Limite: R$ {limite_inicial:,.2f} a R$ {limite_final:,.2f}")
            print(f"   Alíquota Nominal: {aliquota_nominal*100:.2f}%")
            print(f"   Valor Dedução: R$ {valor_deducao:,.2f}")
            
            return faixa_numero, aliquota_nominal, valor_deducao
    
    print(f"⚠️ ERRO: Faixa não encontrada para RBT12 = R$ {rbt12:,.2f}")
    return None, None, None

def calcular_aliquota_apurada(rbt12, anexo_simples_data):
    """
    INSTRUÇÃO OBRIGATÓRIA PARA TODOS OS MESES:
    
    A ALÍQUOTA APURADA DEVE ser sempre calculada usando a fórmula oficial do Simples Nacional:
    
    ALÍQUOTA APURADA = (RBT12 × ALÍQUOTA NOMINAL - VALOR DEDUÇÃO) / RBT12
    
    ONDE:
    - RBT12 = Receita Bruta dos 12 meses anteriores (do PGDAS)
    - ALÍQUOTA NOMINAL = Alíquota da faixa correspondente (Anexo I do Simples)
    - VALOR DEDUÇÃO = Valor a deduzir da faixa correspondente (Anexo I do Simples)
    
    REGRAS OBRIGATÓRIAS:
    1. NUNCA usar valores de "aliquota_efetiva" dos arquivos JSON
    2. SEMPRE calcular a ALÍQUOTA APURADA usando a fórmula acima
    3. Buscar alíquota nominal e dedução na tabela do Anexo I conforme RBT12
    4. Aplicar esta ALÍQUOTA APURADA nos tributos de produtos não-monofásicos
    5. Para produtos monofásicos: PIS = 0, COFINS = 0 (independente da alíquota)
    
    TERMINOLOGIA: Use "ALÍQUOTA APURADA" em todos os relatórios para distinguir do valor pré-calculado.
    """
    
    # ✅ BUSCAR DINAMICAMENTE na tabela do Anexo do Simples
    faixa, aliquota_nominal, valor_deducao = identificar_faixa_tributacao(rbt12, anexo_simples_data)
    
    if aliquota_nominal is None or valor_deducao is None:
        print("❌ ERRO: Não foi possível identificar faixa de tributação")
        return None, None, None
    
    # ✅ APLICAR A FÓRMULA OFICIAL
    aliquota_apurada = ((rbt12 * aliquota_nominal) - valor_deducao) / rbt12
    
    print(f"📐 CÁLCULO DA ALÍQUOTA APURADA:")
    print(f"   Fórmula: (RBT12 × Alíquota Nominal - Valor Dedução) / RBT12")
    print(f"   Cálculo: (R$ {rbt12:,.2f} × {aliquota_nominal*100:.2f}% - R$ {valor_deducao:,.2f}) / R$ {rbt12:,.2f}")
    print(f"   Resultado: {aliquota_apurada*100:.4f}%")
    
    return aliquota_apurada, aliquota_nominal, valor_deducao

def obter_proporcoes_tributos(anexo_simples_data, faixa_numero):
    """
    Obtém as proporções de PIS e COFINS da segunda tabela do Anexo do Simples.
    
    REGRA IMPORTANTE:
    As proporções são aplicadas SOBRE A ALÍQUOTA APURADA, não sobre a receita.
    
    Exemplo: Se ALÍQUOTA APURADA = 8,05% e empresa na 4ª faixa:
    - PIS = 2,76% da alíquota apurada = 8,05% × 2,76% = 0,22%
    - COFINS = 12,74% da alíquota apurada = 8,05% × 12,74% = 1,03%
    """
    if not anexo_simples_data or "proporcoes_anexo_1" not in anexo_simples_data:
        print("⚠️ Proporções não encontradas no Anexo, usando do PGDAS")
        return None, None
    
    proporcoes = anexo_simples_data["proporcoes_anexo_1"]
    
    for item in proporcoes:
        if item.get("faixa") == faixa_numero:
            pis_prop = item.get("pis", 0) / 100  # Converte para decimal
            cofins_prop = item.get("cofins", 0) / 100  # Converte para decimal
            
            print(f"📊 Proporções da Faixa {faixa_numero} (aplicadas sobre a Alíquota Apurada):")
            print(f"   PIS: {pis_prop*100:.2f}% da alíquota apurada")
            print(f"   COFINS: {cofins_prop*100:.2f}% da alíquota apurada")
            
            return pis_prop, cofins_prop
    
    print(f"⚠️ Proporções não encontradas para faixa {faixa_numero}")
    return None, None

def classificar_produtos_por_ncm():
    """
    Classifica produtos como monofásicos ou não-monofásicos baseado no NCM
    seguindo rigorosamente a metodologia Fórmula V12.
    """
    # Carregar dados necessários
    ncms_monofasicos = carregar_espelho_ncm_monofasica()
    pgdas_data = carregar_dados_pgdas()
    anexo_simples_data = carregar_anexo_simples()
    
    print(f"📋 Carregados {len(ncms_monofasicos)} NCMs monofásicos do espelho")
    
    if not pgdas_data:
        print("❌ Não foi possível carregar dados do PGDAS")
        return None
    
    if not anexo_simples_data:
        print("❌ Não foi possível carregar dados do Anexo do Simples")
        return None
    
    # Dados do PGDAS
    rbt12 = pgdas_data.get("receita_bruta_acumulada", 0)
    tributos_pgdas = pgdas_data.get("tributos", {})
    
    # ✅ CALCULAR ALÍQUOTA APURADA DINAMICAMENTE
    resultado_aliquota = calcular_aliquota_apurada(rbt12, anexo_simples_data)
    if resultado_aliquota[0] is None:
        return None
    
    aliquota_apurada, aliquota_nominal, valor_deducao = resultado_aliquota
    
    # Identificar faixa para buscar proporções
    faixa_numero, _, _ = identificar_faixa_tributacao(rbt12, anexo_simples_data)
    
    # ✅ BUSCAR PROPORÇÕES DO ANEXO DO SIMPLES
    pis_prop, cofins_prop = obter_proporcoes_tributos(anexo_simples_data, faixa_numero)
    
    # Se não encontrar no Anexo, usar do PGDAS como fallback
    if pis_prop is None or cofins_prop is None:
        proporcoes_pgdas = pgdas_data.get("proporcoes", {})
        pis_prop = proporcoes_pgdas.get("pis", 0.0136)  # 1,36% padrão
        cofins_prop = proporcoes_pgdas.get("cofins", 0.0629)  # 6,29% padrão
        print(f"📊 Usando proporções do PGDAS: PIS {pis_prop*100:.2f}%, COFINS {cofins_prop*100:.2f}%")
    
    print(f"💡 ALÍQUOTA APURADA CALCULADA: {aliquota_apurada*100:.4f}%")
    print(f"   (RBT12: R$ {rbt12:,.2f} × {aliquota_nominal*100}% - R$ {valor_deducao:,.2f}) / R$ {rbt12:,.2f}")
    
    # Contadores
    total_itens = 0
    itens_monofasicos = 0
    itens_nao_monofasicos = 0
    
    # Listas para armazenar exemplos
    exemplos_monofasicos = []
    exemplos_nao_monofasicos = []
    
    # Totais de receita
    rvm_total = 0  # Receita de produtos monofásicos
    rvn_total = 0  # Receita de produtos não-monofásicos
    rbv_total = 0  # Receita bruta de vendas (com desconto)
    rbd_total = 0  # Receita bruta sem desconto
    
    print("🔍 Processando XMLs...")
    
    for arquivo in os.listdir(DIR_XMLS):
        if not arquivo.endswith('.xml'):
            continue
            
        caminho_completo = os.path.join(DIR_XMLS, arquivo)
        
        try:
            # Analisar XML
            tree = ET.parse(caminho_completo)
            root = tree.getroot()
            
            # Encontrar o elemento NFe (pode estar dentro de nfeProc)
            nfe = root
            if root.tag.endswith('nfeProc'):
                for child in root:
                    if child.tag.endswith('NFe'):
                        nfe = child
                        break
                        
            # Namespace para pesquisa de elementos
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Encontrar infNFe
            info_nfe = nfe.find('.//nfe:infNFe', ns)
            if info_nfe is None:
                continue
            
            # Valor total da NF (já considera descontos)
            total_elem = info_nfe.find('.//nfe:total/nfe:ICMSTot/nfe:vNF', ns)
            if total_elem is not None:
                rbv_total += float(total_elem.text)
                
            # Processar itens
            for det in info_nfe.findall('.//nfe:det', ns):
                prod = det.find('.//nfe:prod', ns)
                if prod is None:
                    continue
                    
                # Extrair dados do produto
                ncm = prod.find('.//nfe:NCM', ns)
                ncm_text = ncm.text if ncm is not None else ""
                
                descricao_elem = prod.find('.//nfe:xProd', ns)
                descricao = descricao_elem.text if descricao_elem is not None else ""
                
                vprod_elem = prod.find('.//nfe:vProd', ns)
                vprod = float(vprod_elem.text) if vprod_elem is not None else 0
                
                vdesc_elem = prod.find('.//nfe:vDesc', ns)
                vdesc = float(vdesc_elem.text) if vdesc_elem is not None else 0
                
                # Valor líquido do item (vProd - vDesc)
                valor_liquido = vprod - vdesc
                
                # Atualizar totais
                total_itens += 1
                rbd_total += vprod
                
                # 🔍 CLASSIFICAÇÃO SEGUNDO FÓRMULA V12:
                # Critério: Compare NCM com "Espelho de NCM monofásica"
                is_monofasico = ncm_text in ncms_monofasicos
                
                if is_monofasico:
                    # Produto MONOFÁSICO
                    itens_monofasicos += 1
                    rvm_total += valor_liquido
                    
                    if len(exemplos_monofasicos) < 5:
                        exemplos_monofasicos.append({
                            "ncm": ncm_text,
                            "descricao": descricao,
                            "vprod": vprod,
                            "vdesc": vdesc,
                            "valor_liquido": valor_liquido,
                            "arquivo": arquivo,
                            "classificacao": "MONOFÁSICO (NCM no espelho)"
                        })
                else:
                    # Produto NÃO-MONOFÁSICO
                    itens_nao_monofasicos += 1
                    rvn_total += valor_liquido
                    
                    if len(exemplos_nao_monofasicos) < 5:
                        exemplos_nao_monofasicos.append({
                            "ncm": ncm_text,
                            "descricao": descricao,
                            "vprod": vprod,
                            "vdesc": vdesc,
                            "valor_liquido": valor_liquido,
                            "arquivo": arquivo,
                            "classificacao": "NÃO-MONOFÁSICO (NCM não consta no espelho)"
                        })
        
        except Exception as e:
            print(f"⚠️ Erro ao processar {arquivo}: {str(e)}")
            continue
    
    # 💰 CÁLCULO DOS TRIBUTOS CONFORME V12
    print("\n💰 CALCULANDO TRIBUTOS...")
    print(f"📋 METODOLOGIA:")
    print(f"   • Monofásicos: PIS = 0, COFINS = 0")
    print(f"   • Não-Monofásicos: Receita × Alíquota Apurada × Proporção")
    print(f"   • Proporções aplicadas SOBRE a Alíquota Apurada")
    
    # Para produtos MONOFÁSICOS: PIS = 0, COFINS = 0
    pis_monofasicos = 0.0
    cofins_monofasicos = 0.0
    
    # Para produtos NÃO-MONOFÁSICOS: 
    # Fórmula: RVN × (ALÍQUOTA APURADA × PROPORÇÃO)
    # Exemplo: RVN × (8,05% × 2,76%) para PIS
    aliquota_pis_efetiva = aliquota_apurada * pis_prop
    aliquota_cofins_efetiva = aliquota_apurada * cofins_prop
    
    pis_nao_monofasicos = rvn_total * aliquota_pis_efetiva
    cofins_nao_monofasicos = rvn_total * aliquota_cofins_efetiva
    
    print(f"\n🧮 CÁLCULO DETALHADO:")
    print(f"   Alíquota Apurada: {aliquota_apurada*100:.4f}%")
    print(f"   Proporção PIS: {pis_prop*100:.2f}% → Alíquota PIS Efetiva: {aliquota_pis_efetiva*100:.4f}%")
    print(f"   Proporção COFINS: {cofins_prop*100:.2f}% → Alíquota COFINS Efetiva: {aliquota_cofins_efetiva*100:.4f}%")
    print(f"   RVN (Não-Monofásicos): R$ {rvn_total:,.2f}")
    print(f"   PIS = R$ {rvn_total:,.2f} × {aliquota_pis_efetiva*100:.4f}% = R$ {pis_nao_monofasicos:.2f}")
    print(f"   COFINS = R$ {rvn_total:,.2f} × {aliquota_cofins_efetiva*100:.4f}% = R$ {cofins_nao_monofasicos:.2f}")
    
    # Total apurado
    pis_apurado = pis_monofasicos + pis_nao_monofasicos
    cofins_apurado = cofins_monofasicos + cofins_nao_monofasicos
    
    # Crédito tributário = Declarado - Apurado
    credito_pis = tributos_pgdas.get("pis", 0) - pis_apurado
    credito_cofins = tributos_pgdas.get("cofins", 0) - cofins_apurado
    credito_total = credito_pis + credito_cofins
    
    return {
        "pgdas": pgdas_data,
        "anexo_simples": anexo_simples_data,
        "faixa_tributacao": faixa_numero,
        "aliquota_apurada": aliquota_apurada,
        "aliquota_nominal": aliquota_nominal,
        "valor_deducao": valor_deducao,
        "proporcoes": {
            "pis": pis_prop,
            "cofins": cofins_prop,
            "aliquota_pis_efetiva": aliquota_pis_efetiva,
            "aliquota_cofins_efetiva": aliquota_cofins_efetiva
        },
        "totais": {
            "total_itens": total_itens,
            "itens_monofasicos": itens_monofasicos,
            "itens_nao_monofasicos": itens_nao_monofasicos,
            "rvm_total": rvm_total,
            "rvn_total": rvn_total,
            "rbv_total": rbv_total,
            "rbd_total": rbd_total
        },
        "tributos": {
            "pis_monofasicos": pis_monofasicos,
            "cofins_monofasicos": cofins_monofasicos,
            "pis_nao_monofasicos": pis_nao_monofasicos,
            "cofins_nao_monofasicos": cofins_nao_monofasicos,
            "pis_apurado": pis_apurado,
            "cofins_apurado": cofins_apurado,
            "credito_pis": credito_pis,
            "credito_cofins": credito_cofins,
            "credito_total": credito_total
        },
        "exemplos_monofasicos": exemplos_monofasicos,
        "exemplos_nao_monofasicos": exemplos_nao_monofasicos
    }

def main():
    print("=" * 80)
    print("🔧 TAXENGINE V12 - CLASSIFICAÇÃO E CÁLCULO COM ALÍQUOTA APURADA")
    print("📋 Critério: Comparação NCM vs Espelho + Cálculo Correto de Tributos")
    print("✅ CORREÇÃO: Busca dinâmica na tabela do Anexo do Simples")
    print("=" * 80)
    
    resultados = classificar_produtos_por_ncm()
    
    if not resultados:
        print("❌ Não foi possível processar os dados")
        return
    
    # Dados do PGDAS
    pgdas = resultados["pgdas"]
    print(f"\n📊 DADOS DO PGDAS:")
    print(f"Período: {pgdas.get('periodo')}")
    print(f"CNPJ: {pgdas.get('cnpj')}")
    print(f"RBT12: R$ {pgdas.get('receita_bruta_acumulada', 0):,.2f}")
    print(f"Receita PA: R$ {pgdas.get('receita_bruta_mensal', 0):,.2f}")
    
    # Alíquota Apurada
    print(f"\n⚖️ ALÍQUOTA APURADA (CALCULADA DINAMICAMENTE):")
    print(f"Faixa de Tributação: {resultados['faixa_tributacao']}")
    print(f"Alíquota Nominal: {resultados['aliquota_nominal']*100:.2f}%")
    print(f"Valor Dedução: R$ {resultados['valor_deducao']:,.2f}")
    print(f"ALÍQUOTA APURADA: {resultados['aliquota_apurada']*100:.4f}%")
    print(f"❌ Ignorado 'aliquota_efetiva' do JSON: {pgdas.get('aliquota_efetiva', 0)*100:.2f}%")
    
    # Proporções utilizadas
    proporcoes = resultados["proporcoes"]
    print(f"\n📊 PROPORÇÕES E ALÍQUOTAS EFETIVAS:")
    print(f"Proporção PIS: {proporcoes['pis']*100:.2f}% da Alíquota Apurada")
    print(f"Proporção COFINS: {proporcoes['cofins']*100:.2f}% da Alíquota Apurada")
    print(f"→ Alíquota PIS Efetiva: {proporcoes['aliquota_pis_efetiva']*100:.4f}%")
    print(f"→ Alíquota COFINS Efetiva: {proporcoes['aliquota_cofins_efetiva']*100:.4f}%")
    
    # Resumo dos produtos
    print(f"\n📊 RESUMO DOS PRODUTOS:")
    print("-" * 50)
    totais = resultados["totais"]
    print(f"Total de itens processados: {totais['total_itens']:,}")
    print(f"Itens monofásicos: {totais['itens_monofasicos']:,} ({totais['itens_monofasicos']/totais['total_itens']*100:.1f}%)")
    print(f"Itens não-monofásicos: {totais['itens_nao_monofasicos']:,} ({totais['itens_nao_monofasicos']/totais['total_itens']*100:.1f}%)")
    
    print(f"\n💰 RECEITAS CALCULADAS:")
    print(f"RBV (Receita Bruta de Vendas): R$ {totais['rbv_total']:,.2f}")
    print(f"RBD (Receita sem Descontos): R$ {totais['rbd_total']:,.2f}")
    print(f"RVM (Receita Monofásicos): R$ {totais['rvm_total']:,.2f} ({totais['rvm_total']/totais['rbv_total']*100:.1f}%)")
    print(f"RVN (Receita Não-Monofásicos): R$ {totais['rvn_total']:,.2f} ({totais['rvn_total']/totais['rbv_total']*100:.1f}%)")
    
    # Verificação de consistência
    print(f"\n🔍 VERIFICAÇÃO:")
    diferenca = abs((totais['rvm_total'] + totais['rvn_total']) - totais['rbv_total'])
    print(f"RVM + RVN = R$ {(totais['rvm_total'] + totais['rvn_total']):,.2f}")
    print(f"Diferença com RBV: R$ {diferenca:.2f}")
    
    if diferenca > 1:
        print("⚠️ ATENÇÃO: Diferença significativa detectada!")
    else:
        print("✅ Valores consistentes")
    
    # Cálculo dos tributos
    tributos = resultados["tributos"]
    print(f"\n💸 CÁLCULO DOS TRIBUTOS:")
    print("-" * 50)
    print(f"📈 PIS:")
    print(f"  Declarado (PGDAS): R$ {pgdas.get('tributos', {}).get('pis', 0):.2f}")
    print(f"  Apurado Monofásicos: R$ {tributos['pis_monofasicos']:.2f}")
    print(f"  Apurado Não-Monofásicos: R$ {tributos['pis_nao_monofasicos']:.2f}")
    print(f"  Total Apurado: R$ {tributos['pis_apurado']:.2f}")
    print(f"  💰 CRÉDITO PIS: R$ {tributos['credito_pis']:.2f}")
    
    print(f"\n📈 COFINS:")
    print(f"  Declarado (PGDAS): R$ {pgdas.get('tributos', {}).get('cofins', 0):.2f}")
    print(f"  Apurado Monofásicos: R$ {tributos['cofins_monofasicos']:.2f}")
    print(f"  Apurado Não-Monofásicos: R$ {tributos['cofins_nao_monofasicos']:.2f}")
    print(f"  Total Apurado: R$ {tributos['cofins_apurado']:.2f}")
    print(f"  💰 CRÉDITO COFINS: R$ {tributos['credito_cofins']:.2f}")
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"💰 CRÉDITO TOTAL: R$ {tributos['credito_total']:.2f}")
    
    # Exemplos de produtos monofásicos
    if resultados["exemplos_monofasicos"]:
        print(f"\n🔵 EXEMPLOS DE PRODUTOS MONOFÁSICOS ({len(resultados['exemplos_monofasicos'])}):")
        for i, exemplo in enumerate(resultados["exemplos_monofasicos"], 1):
            print(f"\n{i}. NCM: {exemplo['ncm']}")
            print(f"   Descrição: {exemplo['descricao'][:60]}...")
            print(f"   Valor Produto: R$ {exemplo['vprod']:.2f}")
            print(f"   Desconto: R$ {exemplo['vdesc']:.2f}")
            print(f"   Valor Líquido: R$ {exemplo['valor_liquido']:.2f}")
            print(f"   Classificação: {exemplo['classificacao']}")
    
    # Exemplos de produtos não-monofásicos
    if resultados["exemplos_nao_monofasicos"]:
        print(f"\n🔴 EXEMPLOS DE PRODUTOS NÃO-MONOFÁSICOS ({len(resultados['exemplos_nao_monofasicos'])}):")
        for i, exemplo in enumerate(resultados["exemplos_nao_monofasicos"], 1):
            print(f"\n{i}. NCM: {exemplo['ncm']}")
            print(f"   Descrição: {exemplo['descricao'][:60]}...")
            print(f"   Valor Produto: R$ {exemplo['vprod']:.2f}")
            print(f"   Desconto: R$ {exemplo['vdesc']:.2f}")
            print(f"   Valor Líquido: R$ {exemplo['valor_liquido']:.2f}")
            print(f"   Classificação: {exemplo['classificacao']}")

if __name__ == "__main__":
    main()