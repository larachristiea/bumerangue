import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from core.domain.tabelas import verificar_ncm_monofasico as verificar_ncm

# Classe para armazenar dados da nota fiscal
class NotaFiscal:
    def __init__(self):
        self.chave_acesso = ""
        self.numero = ""
        self.serie = ""
        self.data_emissao = None
        self.cnpj_emitente = ""
        self.nome_emitente = ""
        self.valor_total = 0.0
        self.valor_produtos = 0.0
        self.itens = []
    
    def __str__(self):
        return f"NF-e: {self.numero}-{self.serie} | Emitente: {self.nome_emitente} | Total: R$ {self.valor_total:.2f}"
    
    def to_dict(self):
        return {
            "chave_acesso": self.chave_acesso,
            "numero": self.numero,
            "serie": self.serie,
            "data_emissao": self.data_emissao.strftime("%Y-%m-%d") if self.data_emissao else None,
            "cnpj_emitente": self.cnpj_emitente,
            "nome_emitente": self.nome_emitente,
            "valor_total": self.valor_total,
            "valor_produtos": self.valor_produtos,
            "itens": [item.to_dict() for item in self.itens]
        }

# Classe para armazenar dados do item da nota fiscal
class ItemNotaFiscal:
    def __init__(self):
        self.numero = 0
        self.codigo = ""
        self.descricao = ""
        self.ncm = ""
        self.cfop = ""
        self.quantidade = 0.0
        self.valor_unitario = 0.0
        self.valor_bruto = 0.0  # Valor bruto do produto (vProd)
        self.valor_desconto = 0.0  # Valor de descontos aplicados
        self.valor_total = 0.0  # Valor líquido (bruto - descontos)
        self.pis_cst = ""
        self.pis_valor = 0.0
        self.cofins_cst = ""
        self.cofins_valor = 0.0
        self.tipo_tributario = ""  # "Monofasico" ou "NaoMonofasico"
    
    def __str__(self):
        return f"Item {self.numero}: {self.descricao} | NCM: {self.ncm} | CST PIS: {self.pis_cst} | CST COFINS: {self.cofins_cst} | Tipo: {self.tipo_tributario}"
    
    def to_dict(self):
        return {
            "numero": self.numero,
            "codigo": self.codigo,
            "descricao": self.descricao,
            "ncm": self.ncm,
            "cfop": self.cfop,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "valor_bruto": self.valor_bruto,
            "valor_desconto": self.valor_desconto,
            "valor_total": self.valor_total,
            "pis_cst": self.pis_cst,
            "pis_valor": self.pis_valor,
            "cofins_cst": self.cofins_cst,
            "cofins_valor": self.cofins_valor,
            "tipo_tributario": self.tipo_tributario
        }

# Função para converter string para número
def to_float(value):
    if value is None:
        return 0.0
    
    try:
        # Substituir vírgula por ponto e converter para float
        return float(str(value).replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0

# Função para classificar produto por CSTs
def classificar_por_cst(pis_cst, cofins_cst):
    # CSTs que indicam monofásico
    csts_monofasicos = ['04', '05', '06']
    
    # Verificar se qualquer um dos CSTs está na lista de monofásicos
    if pis_cst in csts_monofasicos or cofins_cst in csts_monofasicos:
        return "Monofasico"
    
    return "NaoMonofasico"

# Esta função será substituída pela implementação em tabelas.py
def verificar_ncm_monofasico(ncm, tabela_ncm=None):
    # Função mantida para compatibilidade, mas será substituída
    return None

# Função para encontrar elementos no XML independente de namespace
def find_element(element, tag_name):
    if element is None:
        return None
    
    # Tenta encontrar o elemento diretamente
    for child in element:
        if child.tag.endswith(tag_name):
            return child
    
    # Procura recursivamente
    for child in element:
        result = find_element(child, tag_name)
        if result is not None:
            return result
    
    return None

# Função para encontrar todos os elementos com uma tag específica
def find_all_elements(element, tag_name):
    results = []
    
    if element is None:
        return results
    
    # Verifica o elemento atual
    if element.tag.endswith(tag_name):
        results.append(element)
    
    # Procura em todos os filhos
    for child in element:
        results.extend(find_all_elements(child, tag_name))
    
    return results

# Função para obter o texto de um elemento
def get_element_text(element, tag_name, default=""):
    found = find_element(element, tag_name)
    return found.text if found is not None and found.text else default

# Função principal para fazer parsing do XML de NFe
def parse_nfe(xml_content, tabela_ncm=None):
    try:
        root = ET.fromstring(xml_content)
        nf = NotaFiscal()
        
        # Encontrar NFe (pode estar dentro de nfeProc)
        nfe = root
        if root.tag.endswith('nfeProc'):
            for child in root:
                if child.tag.endswith('NFe'):
                    nfe = child
                    break
        
        # Encontrar infNFe
        inf_nfe = find_element(nfe, 'infNFe')
        if inf_nfe is None:
            raise Exception("Elemento infNFe não encontrado")
        
        # Extrair ID da nota (chave de acesso)
        nf.chave_acesso = inf_nfe.attrib.get('Id', '').replace('NFe', '')
        
        # Extrair dados de identificação
        ide = find_element(inf_nfe, 'ide')
        if ide is not None:
            nf.numero = get_element_text(ide, 'nNF')
            nf.serie = get_element_text(ide, 'serie')
            
            # Data de emissão
            data_str = get_element_text(ide, 'dhEmi')
            if data_str:
                try:
                    # Formato ISO: 2024-12-01T08:29:12-03:00
                    data_str = data_str.split('T')[0]  # Pega apenas a data
                    nf.data_emissao = datetime.strptime(data_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Extrair dados do emitente
        emit = find_element(inf_nfe, 'emit')
        if emit is not None:
            nf.cnpj_emitente = get_element_text(emit, 'CNPJ')
            nf.nome_emitente = get_element_text(emit, 'xNome')
        
        # Extrair valores totais
        icms_tot = None
        total = find_element(inf_nfe, 'total')
        if total is not None:
            icms_tot = find_element(total, 'ICMSTot')
        
        if icms_tot is not None:
            nf.valor_total = to_float(get_element_text(icms_tot, 'vNF', '0'))
            nf.valor_produtos = to_float(get_element_text(icms_tot, 'vProd', '0'))
        
        # Processar itens (det)
        for det in find_all_elements(inf_nfe, 'det'):
            item = ItemNotaFiscal()
            
            # Número do item
            item.numero = int(det.attrib.get('nItem', '0'))
            
            # Dados do produto
            prod = find_element(det, 'prod')
            if prod is not None:
                item.codigo = get_element_text(prod, 'cProd')
                item.descricao = get_element_text(prod, 'xProd')
                item.ncm = get_element_text(prod, 'NCM')
                item.cfop = get_element_text(prod, 'CFOP')
                item.quantidade = to_float(get_element_text(prod, 'qCom', '0'))
                item.valor_unitario = to_float(get_element_text(prod, 'vUnCom', '0'))
                
                # Armazenar valor bruto do produto
                item.valor_bruto = to_float(get_element_text(prod, 'vProd', '0'))
                
                # Verificar se há descontos aplicados
                item.valor_desconto = to_float(get_element_text(prod, 'vDesc', '0'))
                
                # Calcular o valor líquido (valor bruto - desconto)
                item.valor_total = item.valor_bruto - item.valor_desconto
            
            # Dados de impostos
            imposto = find_element(det, 'imposto')
            if imposto is not None:
                # PIS
                pis = find_element(imposto, 'PIS')
                if pis is not None:
                    # Buscar CST em grupos de PIS (PISAliq, PISNT, PISOutr, etc.)
                    pis_grupo = None
                    for child in pis:
                        # Detectar se é um grupo PIS
                        if child.tag.endswith('Aliq') or child.tag.endswith('NT') or child.tag.endswith('Outr') or child.tag.endswith('Qtde'):
                            pis_grupo = child
                            break
                    
                    if pis_grupo is not None:
                        item.pis_cst = get_element_text(pis_grupo, 'CST')
                        item.pis_valor = to_float(get_element_text(pis_grupo, 'vPIS', '0'))
                
                # COFINS
                cofins = find_element(imposto, 'COFINS')
                if cofins is not None:
                    # Buscar CST em grupos de COFINS (COFINSAliq, COFINSNT, COFINSOutr, etc.)
                    cofins_grupo = None
                    for child in cofins:
                        # Detectar se é um grupo COFINS
                        if child.tag.endswith('Aliq') or child.tag.endswith('NT') or child.tag.endswith('Outr') or child.tag.endswith('Qtde'):
                            cofins_grupo = child
                            break
                    
                    if cofins_grupo is not None:
                        item.cofins_cst = get_element_text(cofins_grupo, 'CST')
                        item.cofins_valor = to_float(get_element_text(cofins_grupo, 'vCOFINS', '0'))
            
            # Estratégia de classificação:
            # Classificar APENAS pelo NCM usando a tabela de referência (conforme Mecanismo V2)
            eh_monofasico = verificar_ncm(item.ncm)
            if eh_monofasico:
                item.tipo_tributario = "Monofasico"
            else:
                item.tipo_tributario = "NaoMonofasico"
            
            # Adicionar item à nota fiscal
            nf.itens.append(item)
        
        return nf
    
    except Exception as e:
        print(f"Erro ao processar XML: {str(e)}")
        return None

# Função para validar XML
def validar_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)
        
        # Encontrar NFe (pode estar dentro de nfeProc)
        nfe = root
        if root.tag.endswith('nfeProc'):
            for child in root:
                if child.tag.endswith('NFe'):
                    nfe = child
                    break
        
        # Verificar se encontrou NFe
        if not nfe.tag.endswith('NFe'):
            return False
        
        # Verificar elementos essenciais
        inf_nfe = find_element(nfe, 'infNFe')
        if inf_nfe is None:
            return False
        
        # Verificar identificação
        ide = find_element(inf_nfe, 'ide')
        if ide is None:
            return False
        
        # Verificar emitente
        emit = find_element(inf_nfe, 'emit')
        if emit is None:
            return False
        
        return True
    except Exception as e:
        print(f"Erro na validação XML: {str(e)}")
        return False

# Função para carregar dados do PGDAS de um arquivo JSON
def carregar_pgdas(arquivo_json):
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar PGDAS: {str(e)}")
        return None

# Função para processar um diretório de XMLs
def processar_xmls(diretorio, tabela_ncm=None):
    notas = []
    
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith('.xml'):
            caminho_completo = os.path.join(diretorio, arquivo)
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as f:
                    conteudo_xml = f.read()
                
                if validar_xml(conteudo_xml):
                    nota = parse_nfe(conteudo_xml, tabela_ncm)
                    if nota:
                        notas.append(nota)
                        print(f"Processado: {nota}")
                else:
                    print(f"XML inválido: {arquivo}")
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {str(e)}")
    
    return notas

# Função para calcular alíquotas efetivas de PIS e COFINS
def calcular_aliquotas(dados_pgdas):
    aliquota_apurada = dados_pgdas.get("dados_estruturados", {}).get("aliquota_apurada")
    proporcoes = dados_pgdas.get("proporcoes", {})
    
    aliquota_pis = aliquota_apurada * proporcoes.get("pis", 0.0276)
    aliquota_cofins = aliquota_apurada * proporcoes.get("cofins", 0.1274)
    
    return aliquota_pis, aliquota_cofins

# Função para analisar dados e calcular créditos
def calcular_creditos(notas, dados_pgdas):
    # Totais por categoria
    total_monofasico = 0.0
    total_nao_monofasico = 0.0
    
    # Itens por categoria
    itens_monofasicos = []
    itens_nao_monofasicos = []
    
    # Processar cada nota fiscal
    for nf in notas:
        for item in nf.itens:
            # Calcular valor líquido do item (valor bruto - descontos/impostos não aplicáveis)
            # Por simplicidade, estamos considerando o valor_total como o valor líquido base
            # Se houver campos específicos para descontos, eles devem ser subtraídos aqui
            valor_liquido = item.valor_total
            
            if item.tipo_tributario == "Monofasico":
                total_monofasico += valor_liquido
                itens_monofasicos.append(item)
            else:
                total_nao_monofasico += valor_liquido
                itens_nao_monofasicos.append(item)
    
    # Calcular alíquota efetiva de PIS e COFINS
    aliquota_pis, aliquota_cofins = calcular_aliquotas(dados_pgdas)
    
    # Calcular valores devidos sobre produtos não-monofásicos
    # Usar valores líquidos (descontando outros valores que possam ter sido agregados)
    pis_devido = total_nao_monofasico * aliquota_pis
    cofins_devido = total_nao_monofasico * aliquota_cofins
    
    # Calcular créditos tributários (recolhido - devido sobre não-monofásicos)
    tributos = dados_pgdas.get("tributos", {})
    credito_pis = tributos.get("pis", 0) - pis_devido
    credito_cofins = tributos.get("cofins", 0) - cofins_devido
    credito_total = credito_pis + credito_cofins
    
    # Resultados
    resultados = {
        "total_monofasico": total_monofasico,
        "total_nao_monofasico": total_nao_monofasico,
        "proporcao_monofasico": (total_monofasico / (total_monofasico + total_nao_monofasico)) * 100 if (total_monofasico + total_nao_monofasico) > 0 else 0,
        "aliquotas": {
            "aliquota_apurada": dados_pgdas.get("dados_estruturados", {}).get("aliquota_apurada", 0),
            "aliquota_pis": aliquota_pis,
            "aliquota_cofins": aliquota_cofins
        },
        "tributos_recolhidos": {
            "pis": tributos.get("pis", 0),
            "cofins": tributos.get("cofins", 0)
        },
        "tributos_devidos": {
            "pis": pis_devido,
            "cofins": cofins_devido
        },
        "creditos": {
            "pis": credito_pis,
            "cofins": credito_cofins,
            "total": credito_total
        },
        "estatisticas": {
            "qtd_notas": len(notas),
            "qtd_itens_total": len(itens_monofasicos) + len(itens_nao_monofasicos),
            "qtd_itens_monofasicos": len(itens_monofasicos),
            "qtd_itens_nao_monofasicos": len(itens_nao_monofasicos)
        }
    }
    
    # Geração de relatório simples de classificação
    with open('relatorio_classificacao_itens.csv', 'w', encoding='utf-8') as f:
        f.write('Tipo,NCM,Descricao,Valor Total\n')
        for item in itens_monofasicos:
            f.write(f'Monofasico,{item.ncm},"{item.descricao}",{item.valor_total}\n')
        for item in itens_nao_monofasicos:
            f.write(f'NaoMonofasico,{item.ncm},"{item.descricao}",{item.valor_total}\n')
    
    return resultados

# Função para atualizar valor com SELIC
def atualizar_selic(valor, taxa_selic):
    return valor * (1 + taxa_selic)