import os
import json
import xml.etree.ElementTree as ET

# Diretório dos XMLs
DIR_XMLS = "/Users/trkia/Desktop/V12/data/xmls/2024-12-validos"

# Caminho para o arquivo do Espelho de NCM monofásica
ESPELHO_NCM_MONOFASICA = "/Users/trkia/Desktop/V12/data/espelho_ncm_monofasica.txt"  # Ajuste o caminho conforme necessário

def carregar_espelho_ncm_monofasica():
    """
    Carrega a lista de NCMs monofásicos do arquivo espelho.
    Retorna um set com os NCMs para busca rápida.
    """
    try:
        with open(ESPELHO_NCM_MONOFASICA, 'r', encoding='utf-8') as arquivo:
            # Carrega NCMs, removendo espaços e quebras de linha
            ncms_monofasicos = set()
            for linha in arquivo:
                ncm = linha.strip()
                if ncm:  # Ignora linhas vazias
                    ncms_monofasicos.add(ncm)
            return ncms_monofasicos
    except FileNotFoundError:
        print(f"⚠️ ERRO: Arquivo {ESPELHO_NCM_MONOFASICA} não encontrado!")
        print("📋 Criando lista vazia. Verifique o caminho do arquivo.")
        return set()
    except Exception as e:
        print(f"⚠️ ERRO ao carregar espelho de NCM: {str(e)}")
        return set()

def classificar_produtos_por_ncm():
    """
    Classifica produtos como monofásicos ou não-monofásicos baseado no NCM
    seguindo rigorosamente a metodologia Fórmula V12.
    """
    # Carregar espelho de NCMs monofásicos
    ncms_monofasicos = carregar_espelho_ncm_monofasica()
    print(f"📋 Carregados {len(ncms_monofasicos)} NCMs monofásicos do espelho")
    
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
    
    return {
        "totais": {
            "total_itens": total_itens,
            "itens_monofasicos": itens_monofasicos,
            "itens_nao_monofasicos": itens_nao_monofasicos,
            "rvm_total": rvm_total,
            "rvn_total": rvn_total,
            "rbv_total": rbv_total,
            "rbd_total": rbd_total
        },
        "exemplos_monofasicos": exemplos_monofasicos,
        "exemplos_nao_monofasicos": exemplos_nao_monofasicos
    }

def main():
    print("=" * 70)
    print("🔧 FÓRMULA V12 - CLASSIFICAÇÃO DE PRODUTOS MONOFÁSICOS")
    print("📋 Critério: Comparação NCM vs Espelho de NCM monofásica")
    print("=" * 70)
    
    resultados = classificar_produtos_por_ncm()
    
    print("\n📊 RESUMO DOS RESULTADOS:")
    print("-" * 50)
    totais = resultados["totais"]
    print(f"Total de itens processados: {totais['total_itens']:,}")
    print(f"Itens monofásicos: {totais['itens_monofasicos']:,}")
    print(f"Itens não-monofásicos: {totais['itens_nao_monofasicos']:,}")
    
    print(f"\n💰 RECEITAS CALCULADAS:")
    print(f"RBV (Receita Bruta de Vendas): R$ {totais['rbv_total']:,.2f}")
    print(f"RBD (Receita sem Descontos): R$ {totais['rbd_total']:,.2f}")
    print(f"RVM (Receita Monofásicos): R$ {totais['rvm_total']:,.2f}")
    print(f"RVN (Receita Não-Monofásicos): R$ {totais['rvn_total']:,.2f}")
    
    # Verificação de consistência
    print(f"\n🔍 VERIFICAÇÃO:")
    diferenca = abs((totais['rvm_total'] + totais['rvn_total']) - totais['rbv_total'])
    print(f"RVM + RVN = R$ {(totais['rvm_total'] + totais['rvn_total']):,.2f}")
    print(f"Diferença com RBV: R$ {diferenca:.2f}")
    
    if diferenca > 1:  # Tolerância de R$ 1,00
        print("⚠️ ATENÇÃO: Diferença significativa detectada!")
    else:
        print("✅ Valores consistentes")
    
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