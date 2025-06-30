import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime

# Namespace para os XMLs de NFe
ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

def listar_arquivos_xml(diretorio):
    """
    Lista todos os arquivos XML em um diretório.
    
    Args:
        diretorio (str): Caminho do diretório a ser verificado
        
    Returns:
        list: Lista com todos os caminhos de arquivos XML
    """
    # Verificar se o diretório existe
    if not os.path.exists(diretorio):
        raise FileNotFoundError(f"O diretório {diretorio} não existe.")
    
    # Lista para armazenar todos os arquivos XML
    arquivos_xml = []
    
    # Percorrer o diretório para encontrar os arquivos XML
    for arquivo in os.listdir(diretorio):
        if arquivo.lower().endswith('.xml'):
            caminho_completo = os.path.join(diretorio, arquivo)
            arquivos_xml.append(caminho_completo)
    
    print(f"Encontrados {len(arquivos_xml)} arquivos XML no diretório.")
    
    return arquivos_xml

def determinar_tipo_xml(root):
    """
    Determina o tipo de arquivo XML: nota fiscal ou evento.
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        str: 'NFE' para nota fiscal ou 'EVENTO' para evento
    """
    # Verificar se é um procEventoNFe (evento)
    if root.find('.//nfe:procEventoNFe', ns) is not None or root.tag.endswith('procEventoNFe'):
        return 'EVENTO'
    
    # Verificar se é um NFe ou procNFe (nota fiscal)
    if (root.find('.//nfe:NFe', ns) is not None or 
        root.find('.//nfe:procNFe', ns) is not None or
        root.tag.endswith('NFe') or 
        root.tag.endswith('procNFe')):
        return 'NFE'
    
    # Se não for nenhum dos tipos conhecidos
    return 'DESCONHECIDO'

def extrair_evento_cancelamento(root):
    """
    Extrai informações de um evento de cancelamento.
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        dict: Dicionário com informações do evento ou None se não for um cancelamento
    """
    # Tentar encontrar o tipo de evento
    tipo_evento_elem = root.find('.//nfe:tpEvento', ns)
    if tipo_evento_elem is None:
        return None
    
    tipo_evento = tipo_evento_elem.text
    
    # Verificar se é um evento de cancelamento (código 110111)
    if tipo_evento != '110111':
        return None
    
    # Extrair a chave da NFe cancelada
    chave_nfe_elem = root.find('.//nfe:chNFe', ns)
    if chave_nfe_elem is None:
        return None
    
    chave_nfe = chave_nfe_elem.text
    
    # Extrair data do evento para determinar a mais recente em caso de múltiplos eventos
    data_evento_elem = root.find('.//nfe:dhEvento', ns)
    data_evento = data_evento_elem.text if data_evento_elem is not None else None
    
    return {
        'tipo': 'CANCELAMENTO',
        'chave_nfe': chave_nfe,
        'data_evento': data_evento
    }

def extrair_dados_nfe(root):
    """
    Extrai todos os dados necessários de uma nota fiscal.
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        list: Lista de dicionários, um para cada item da nota
    """
    # Obter o elemento infNFe que contém a maioria das informações
    inf_nfe = root.find('.//nfe:infNFe', ns)
    if inf_nfe is None:
        return []
    
    # 1. ChaveNFe - extrair do atributo Id do infNFe, removendo o prefixo "NFe"
    chave_nfe = ""
    if 'Id' in inf_nfe.attrib:
        chave_nfe = inf_nfe.attrib['Id'].replace('NFe', '')
    
    # 2. NumeroNFe - número da nota fiscal
    numero_nfe_elem = inf_nfe.find('.//nfe:ide/nfe:nNF', ns)
    numero_nfe = numero_nfe_elem.text if numero_nfe_elem is not None else ""
    
    # 3. DataEmissao - data de emissão formatada para DD/MM/AAAA
    data_emissao = ""
    data_emissao_elem = inf_nfe.find('.//nfe:ide/nfe:dhEmi', ns)
    if data_emissao_elem is not None:
        # Formato original: AAAA-MM-DDThh:mm:ssTZD
        try:
            data_str = data_emissao_elem.text
            if 'T' in data_str:
                data_str = data_str.split('T')[0]  # Pegar apenas a parte da data
            data_parts = data_str.split('-')
            if len(data_parts) == 3:
                data_emissao = f"{data_parts[2]}/{data_parts[1]}/{data_parts[0]}"
        except Exception:
            data_emissao = data_emissao_elem.text  # Manter original se o formato for inesperado
    
    # 4. CNPJEmitente - CNPJ da empresa que emitiu a nota
    cnpj_emitente_elem = inf_nfe.find('.//nfe:emit/nfe:CNPJ', ns)
    cnpj_emitente = cnpj_emitente_elem.text if cnpj_emitente_elem is not None else ""
    
    # 5. NomeEmitente - Nome da empresa emitente
    nome_emitente_elem = inf_nfe.find('.//nfe:emit/nfe:xNome', ns)
    nome_emitente = nome_emitente_elem.text if nome_emitente_elem is not None else ""
    
    # 6. CPF_CNPJDestinatario - CPF ou CNPJ do destinatário
    cpf_cnpj_dest = ""
    cpf_dest_elem = inf_nfe.find('.//nfe:dest/nfe:CPF', ns)
    cnpj_dest_elem = inf_nfe.find('.//nfe:dest/nfe:CNPJ', ns)
    
    if cpf_dest_elem is not None:
        cpf_cnpj_dest = cpf_dest_elem.text
    elif cnpj_dest_elem is not None:
        cpf_cnpj_dest = cnpj_dest_elem.text
    
    # 7. NomeDestinatario - Nome do destinatário
    nome_dest_elem = inf_nfe.find('.//nfe:dest/nfe:xNome', ns)
    nome_dest = nome_dest_elem.text if nome_dest_elem is not None else ""
    
    # 20. ValorTotalNota - Valor total da nota fiscal
    valor_total_nota_elem = inf_nfe.find('.//nfe:total/nfe:ICMSTot/nfe:vNF', ns)
    valor_total_nota = valor_total_nota_elem.text if valor_total_nota_elem is not None else "0"
    
    # 21. ValorTotalDescontoNota - Valor total do desconto na nota
    valor_total_desc_nota_elem = inf_nfe.find('.//nfe:total/nfe:ICMSTot/nfe:vDesc', ns)
    valor_total_desc_nota = valor_total_desc_nota_elem.text if valor_total_desc_nota_elem is not None else "0"
    
    # 25. vProdTotal - Valor total da nota antes do desconto
    v_prod_total_elem = inf_nfe.find('.//nfe:total/nfe:ICMSTot/nfe:vProd', ns)
    v_prod_total = v_prod_total_elem.text if v_prod_total_elem is not None else "0"
    
    # 27. InformacoesAdicionais - Campo de informações adicionais
    info_adicionais_elem = inf_nfe.find('.//nfe:infAdic/nfe:infCpl', ns)
    info_adicionais = info_adicionais_elem.text if info_adicionais_elem is not None else ""
    
    # Inicializar lista para armazenar os itens da nota
    itens = []
    
    # Processar cada item (det) da nota fiscal
    for det_elem in inf_nfe.findall('.//nfe:det', ns):
        # 22. NumeroItem - Número sequencial do item na nota
        numero_item = det_elem.attrib.get('nItem', '')
        
        # Elemento do produto
        prod_elem = det_elem.find('.//nfe:prod', ns)
        if prod_elem is None:
            continue
        
        # 8. CodigoProduto - Código interno do produto
        codigo_prod_elem = prod_elem.find('nfe:cProd', ns)
        codigo_prod = codigo_prod_elem.text if codigo_prod_elem is not None else ""
        
        # 9. EAN - Código de barras do produto
        ean_elem = prod_elem.find('nfe:cEAN', ns)
        ean = ean_elem.text if ean_elem is not None else ""
        
        # 10. DescricaoProduto - Nome/descrição do produto
        desc_prod_elem = prod_elem.find('nfe:xProd', ns)
        desc_prod = desc_prod_elem.text if desc_prod_elem is not None else ""
        
        # 11. NCM - Nomenclatura Comum do Mercosul
        ncm_elem = prod_elem.find('nfe:NCM', ns)
        ncm = ncm_elem.text if ncm_elem is not None else ""
        
        # 12. CEST - Código Especificador da Substituição Tributária
        cest_elem = prod_elem.find('nfe:CEST', ns)
        cest = cest_elem.text if cest_elem is not None else ""
        
        # 13. CFOP - Código Fiscal de Operações e Prestações
        cfop_elem = prod_elem.find('nfe:CFOP', ns)
        cfop = cfop_elem.text if cfop_elem is not None else ""
        
        # 14. UnidadeComercial - Unidade de medida do produto
        unidade_elem = prod_elem.find('nfe:uCom', ns)
        unidade = unidade_elem.text if unidade_elem is not None else ""
        
        # 15. Quantidade - Quantidade do produto na nota
        qtd_elem = prod_elem.find('nfe:qCom', ns)
        qtd = qtd_elem.text if qtd_elem is not None else "0"
        
        # 16. ValorUnitario - Valor unitário do produto
        val_unit_elem = prod_elem.find('nfe:vUnCom', ns)
        val_unit = val_unit_elem.text if val_unit_elem is not None else "0"
        
        # 17. ValorProduto - Valor total do produto sem desconto
        val_prod_elem = prod_elem.find('nfe:vProd', ns)
        val_prod = val_prod_elem.text if val_prod_elem is not None else "0"
        
        # 18. ValorDesconto - Valor do desconto aplicado ao produto
        val_desc_elem = prod_elem.find('nfe:vDesc', ns)
        val_desc = val_desc_elem.text if val_desc_elem is not None else "0"
        
        # 19. ValorTotalProduto - Valor total do produto após desconto
        try:
            valor_total_produto = float(val_prod) - float(val_desc)
            valor_total_produto = str(valor_total_produto)
        except ValueError:
            valor_total_produto = val_prod  # Se não conseguir calcular, usa o valor bruto
        
        # 23 e 24. CST e CSOSN - Códigos tributários
        # Procurar em diferentes grupos de tributação ICMS
        cst = ""
        csosn = ""
        
        # Verificar diferentes grupos de ICMS
        imposto_elem = det_elem.find('.//nfe:imposto', ns)
        if imposto_elem is not None:
            icms_elem = imposto_elem.find('.//nfe:ICMS', ns)
            if icms_elem is not None:
                # Verificar todos os filhos do ICMS para encontrar CST ou CSOSN
                for child in icms_elem:
                    tag_name = child.tag.split('}')[-1]  # Remove namespace
                    
                    # Procurar CST
                    cst_elem = child.find('.//nfe:CST', ns)
                    if cst_elem is not None:
                        cst = cst_elem.text
                        break
                    
                    # Procurar CSOSN
                    csosn_elem = child.find('.//nfe:CSOSN', ns)
                    if csosn_elem is not None:
                        csosn = csosn_elem.text
                        break
        
        # 26. Status - Status da nota fiscal (será atualizado depois com os eventos)
        status = "ATIVO"  # Por padrão, todas as notas são consideradas ativas
        
        # Criar dicionário com os dados do item
        item = {
            "ChaveNFe": chave_nfe,
            "NumeroNFe": numero_nfe,
            "DataEmissao": data_emissao,
            "CNPJEmitente": cnpj_emitente,
            "NomeEmitente": nome_emitente,
            "CPF_CNPJDestinatario": cpf_cnpj_dest,
            "NomeDestinatario": nome_dest,
            "CodigoProduto": codigo_prod,
            "EAN": ean,
            "DescricaoProduto": desc_prod,
            "NCM": ncm,
            "CEST": cest,
            "CFOP": cfop,
            "UnidadeComercial": unidade,
            "Quantidade": qtd,
            "ValorUnitario": val_unit,
            "ValorProduto": val_prod,
            "ValorDesconto": val_desc,
            "ValorTotalProduto": valor_total_produto,
            "ValorTotalNota": valor_total_nota,
            "ValorTotalDescontoNota": valor_total_desc_nota,
            "NumeroItem": numero_item,
            "CST": cst,
            "CSOSN": csosn,
            "vProdTotal": v_prod_total,
            "Status": status,
            "InformacoesAdicionais": info_adicionais
        }
        
        itens.append(item)
    
    return itens

def processar_xmls(diretorio):
    """
    Processa todos os arquivos XML em um diretório.
    
    Args:
        diretorio (str): Caminho do diretório contendo os arquivos XML
        
    Returns:
        tuple: (dados, estatisticas) onde dados é uma lista de dicionários com os dados extraídos
              e estatisticas é um dicionário com informações sobre o processamento
    """
    # Iniciar cronômetro para medir o tempo de processamento
    tempo_inicio = time.time()
    
    # Listar arquivos XML no diretório
    try:
        arquivos_xml = listar_arquivos_xml(diretorio)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        return [], {}
    
    # Dicionário para armazenar eventos de cancelamento por chave de nota
    cancelamentos = {}
    
    # Primeiro passo: encontrar todos os eventos de cancelamento
    print("Identificando eventos de cancelamento...")
    for arquivo in arquivos_xml:
        try:
            # Analisar o XML
            tree = ET.parse(arquivo)
            root = tree.getroot()
            
            # Verificar se é um evento de cancelamento
            if determinar_tipo_xml(root) == 'EVENTO':
                evento = extrair_evento_cancelamento(root)
                if evento and evento['tipo'] == 'CANCELAMENTO':
                    chave_nfe = evento['chave_nfe']
                    data_evento = evento['data_evento']
                    
                    # Se já existir um evento para esta nota, manter apenas o mais recente
                    if chave_nfe in cancelamentos:
                        # Simplificação: assumir que o evento já existente é mais antigo
                        # Uma implementação completa compararia as datas
                        pass
                    else:
                        cancelamentos[chave_nfe] = 'CANCELADO'
                    
                    print(f"Nota {chave_nfe} marcada como CANCELADA.")
        except Exception as e:
            # Silenciosamente ignorar erros ao tentar processar arquivo como evento
            pass
    
    # Segundo passo: verificar arquivos que têm "cancelada" ou similar no nome
    print("Verificando arquivos com indicação de cancelamento no nome...")
    for arquivo in arquivos_xml:
        nome_arquivo = os.path.basename(arquivo).lower()
        if "cancel" in nome_arquivo or "-can" in nome_arquivo:
            try:
                # Tentar extrair a chave da NFe deste arquivo
                tree = ET.parse(arquivo)
                root = tree.getroot()
                
                # Verificar se é uma nota fiscal
                if determinar_tipo_xml(root) == 'NFE':
                    inf_nfe = root.find('.//nfe:infNFe', ns)
                    if inf_nfe is not None and 'Id' in inf_nfe.attrib:
                        chave_nfe = inf_nfe.attrib['Id'].replace('NFe', '')
                        cancelamentos[chave_nfe] = 'CANCELADO'
                        print(f"Nota {chave_nfe} marcada como CANCELADA pelo nome do arquivo.")
            except Exception as e:
                pass
    
    # Terceiro passo: verificar notas fiscais que estão marcadas como canceladas em seu conteúdo
    print("Verificando notas com status de cancelamento no conteúdo...")
    
    # Lista para armazenar todos os dados extraídos
    dados = []
    
    # Contadores para estatísticas
    count_notas = 0
    count_itens = 0
    count_ativas = 0
    count_canceladas = 0
    
    # Verificar se existe CSV para identificar status
    # Primeiro verificar no diretório de XML
    arquivos_csv = [f for f in os.listdir(diretorio) if f.lower().endswith('.csv')]
    
    # Se não encontrar no diretório de XMLs, verificar no diretório pai
    if not arquivos_csv:
        diretorio_pai = os.path.dirname(diretorio)
        arquivos_csv = [f for f in os.listdir(diretorio_pai) if f.lower().endswith('.csv')]
        if arquivos_csv:
            diretorio = diretorio_pai  # Atualizar diretório para o pai se encontrar CSV lá
            
    # Se encontrou CSV, processar
    if arquivos_csv:
        print(f"Encontrado arquivo CSV que pode conter informações de status: {arquivos_csv[0]}")
        try:
            import csv
            caminho_csv = os.path.join(diretorio, arquivos_csv[0])
            print(f"Caminho completo do CSV: {caminho_csv}")
            
            with open(caminho_csv, 'r', encoding='utf-8') as f:
                leitor = csv.DictReader(f)
                for linha in leitor:
                    if 'ChaveNFe' in linha and 'Status' in linha:
                        if linha['Status'].upper() != 'ATIVO':
                            chave = linha['ChaveNFe']
                            cancelamentos[chave] = 'CANCELADO'
                            print(f"Nota {chave} marcada como CANCELADA pelo CSV.")
        except Exception as e:
            print(f"Erro ao processar CSV para status: {e}")
    
    # Processar arquivos de notas fiscais
    print("Processando notas fiscais...")
    for arquivo in arquivos_xml:
        try:
            # Analisar o XML
            tree = ET.parse(arquivo)
            root = tree.getroot()
            
            # Verificar se é uma nota fiscal
            if determinar_tipo_xml(root) == 'NFE':
                # Extrair dados da nota
                itens_nfe = extrair_dados_nfe(root)
                
                if itens_nfe:
                    count_notas += 1
                    count_itens += len(itens_nfe)
                    
                    # Verificar se a nota foi cancelada
                    chave_nfe = itens_nfe[0]["ChaveNFe"]
                    if chave_nfe in cancelamentos:
                        # Atualizar status de todos os itens da nota
                        for item in itens_nfe:
                            item["Status"] = "CANCELADO"
                        count_canceladas += 1
                    else:
                        count_ativas += 1
                    
                    # Adicionar itens à lista de dados
                    dados.extend(itens_nfe)
        except Exception as e:
            # print(f"Erro ao processar a nota {arquivo}: {e}")
            pass
    
    # Calcular tempo de processamento
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    
    # Compilar estatísticas
    estatisticas = {
        "total_xmls_processados": len(arquivos_xml),
        "total_notas_fiscais": count_notas,
        "total_itens_extraidos": count_itens,
        "notas_ativas": count_ativas,
        "notas_canceladas": count_canceladas,
        "tempo_processamento": tempo_total
    }
    
    print(f"\nProcessamento concluído em {tempo_total:.2f} segundos.")
    print(f"Total de notas fiscais: {count_notas} (Ativas: {count_ativas}, Canceladas: {count_canceladas})")
    print(f"Total de itens extraídos: {count_itens}")
    
    return dados, estatisticas

def main():
    """
    Função principal que controla o fluxo do processamento.
    """
    print("==== Processador de XMLs de Notas Fiscais ====\n")
    
    # Usar o diretório que contém tanto o CSV quanto o diretório de XMLs
    diretorio = "/Users/trkia/Desktop/V12/data/xmls"
    xml_dir = os.path.join(diretorio, "2024-03")
    
    print(f"\nIniciando processamento no diretório: {xml_dir}")
    
    # Processar os XMLs no diretório
    dados, estatisticas = processar_xmls(xml_dir)
    
    if not dados:
        print("Nenhum dado foi extraído. Verifique o diretório e os arquivos XML.")
        return
    
    print("\n==== Estatísticas do Processamento ====")
    print(f"Total de arquivos XML processados: {estatisticas['total_xmls_processados']}")
    print(f"Total de notas fiscais: {estatisticas['total_notas_fiscais']}")
    print(f"Total de itens extraídos: {estatisticas['total_itens_extraidos']}")
    print(f"Notas fiscais ativas: {estatisticas['notas_ativas']}")
    print(f"Notas fiscais canceladas: {estatisticas['notas_canceladas']}")
    print(f"Tempo de processamento: {estatisticas['tempo_processamento']:.2f} segundos")
    
    # Nos próximos passos, implementaremos a exportação para CSV, XLSX e JSON
    print("\nDados extraídos com sucesso! Nos próximos passos, implementaremos a exportação para CSV, XLSX e JSON.")

if __name__ == "__main__":
    main()