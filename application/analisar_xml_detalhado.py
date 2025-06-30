#!/usr/bin/env python3
"""
Script para análise detalhada de um arquivo XML de nota fiscal eletrônica.
Este script ajuda a entender a estrutura e valores de um XML específico.
"""

import os
import sys
import xml.etree.ElementTree as ET
import json
from datetime import datetime

def analisar_xml(caminho_xml):
    """Analisa detalhadamente um arquivo XML e exibe sua estrutura e conteúdo"""
    if not os.path.exists(caminho_xml):
        print(f"ERRO: Arquivo não encontrado: {caminho_xml}")
        return False
    
    try:
        tree = ET.parse(caminho_xml)
        root = tree.getroot()
        
        # Detectar namespace automaticamente
        ns = {}
        for prefix, uri in root.attrib.items():
            if prefix.startswith("xmlns:"):
                ns[prefix[6:]] = uri
            elif prefix == "xmlns":
                ns["default"] = uri
        
        # Se não encontrou namespace, usar o padrão da NFe
        if "nfe" not in ns:
            ns["nfe"] = "http://www.portalfiscal.inf.br/nfe"
        
        # 1. Informações básicas da nota
        print("\n" + "="*60)
        print(f"ANÁLISE DETALHADA DO XML: {os.path.basename(caminho_xml)}")
        print("="*60 + "\n")
        
        print("INFORMAÇÕES BÁSICAS:")
        print("-"*40)
        
        # Chave de acesso
        chave = None
        for inf_nfe in root.findall(".//{http://www.portalfiscal.inf.br/nfe}infNFe"):
            if "Id" in inf_nfe.attrib:
                chave = inf_nfe.attrib["Id"].replace("NFe", "")
                break
        
        if not chave:
            for inf_prot in root.findall(".//{http://www.portalfiscal.inf.br/nfe}infProt"):
                ch_nfe = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}chNFe")
                if ch_nfe is not None and ch_nfe.text:
                    chave = ch_nfe.text
                    break
        
        print(f"Chave de acesso: {chave}")
        
        # Data de emissão
        data_emissao = root.find(".//{http://www.portalfiscal.inf.br/nfe}dhEmi")
        if data_emissao is not None:
            print(f"Data de emissão: {data_emissao.text}")
        
        # Status da nota
        status = root.find(".//{http://www.portalfiscal.inf.br/nfe}cStat")
        if status is not None:
            motivo = root.find(".//{http://www.portalfiscal.inf.br/nfe}xMotivo")
            motivo_text = motivo.text if motivo is not None else "Não especificado"
            print(f"Status: {status.text} - {motivo_text}")
        
        # Tipo de operação
        tp_nf = root.find(".//{http://www.portalfiscal.inf.br/nfe}tpNF")
        if tp_nf is not None:
            tipo_op = "Entrada" if tp_nf.text == "0" else "Saída"
            print(f"Tipo de operação: {tipo_op} ({tp_nf.text})")
        
        # 2. Emitente e destinatário
        print("\nEMITENTE E DESTINATÁRIO:")
        print("-"*40)
        
        emit = root.find(".//{http://www.portalfiscal.inf.br/nfe}emit")
        if emit is not None:
            cnpj_emit = emit.find("{http://www.portalfiscal.inf.br/nfe}CNPJ")
            nome_emit = emit.find("{http://www.portalfiscal.inf.br/nfe}xNome")
            if cnpj_emit is not None and nome_emit is not None:
                print(f"Emitente: {nome_emit.text} (CNPJ: {cnpj_emit.text})")
        
        dest = root.find(".//{http://www.portalfiscal.inf.br/nfe}dest")
        if dest is not None:
            cnpj_dest = dest.find("{http://www.portalfiscal.inf.br/nfe}CNPJ")
            cpf_dest = dest.find("{http://www.portalfiscal.inf.br/nfe}CPF")
            nome_dest = dest.find("{http://www.portalfiscal.inf.br/nfe}xNome")
            
            doc_dest = None
            tipo_doc = None
            
            if cnpj_dest is not None:
                doc_dest = cnpj_dest.text
                tipo_doc = "CNPJ"
            elif cpf_dest is not None:
                doc_dest = cpf_dest.text
                tipo_doc = "CPF"
            
            if nome_dest is not None and doc_dest is not None:
                print(f"Destinatário: {nome_dest.text} ({tipo_doc}: {doc_dest})")
        
        # 3. Valores da nota
        print("\nVALORES DA NOTA:")
        print("-"*40)
        
        total = root.find(".//{http://www.portalfiscal.inf.br/nfe}total")
        if total is not None:
            icms_tot = total.find("{http://www.portalfiscal.inf.br/nfe}ICMSTot")
            if icms_tot is not None:
                v_prod = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vProd")
                v_desc = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vDesc")
                v_frete = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vFrete")
                v_seg = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vSeg")
                v_outros = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vOutro")
                v_nf = icms_tot.find("{http://www.portalfiscal.inf.br/nfe}vNF")
                
                print(f"Valor dos produtos: R$ {float(v_prod.text) if v_prod is not None else 0:.2f}")
                print(f"Valor dos descontos: R$ {float(v_desc.text) if v_desc is not None else 0:.2f}")
                print(f"Valor do frete: R$ {float(v_frete.text) if v_frete is not None else 0:.2f}")
                print(f"Valor do seguro: R$ {float(v_seg.text) if v_seg is not None else 0:.2f}")
                print(f"Valor de outras despesas: R$ {float(v_outros.text) if v_outros is not None else 0:.2f}")
                print(f"Valor total da nota: R$ {float(v_nf.text) if v_nf is not None else 0:.2f}")
        
        # 4. Detalhamento dos itens
        itens = root.findall(".//{http://www.portalfiscal.inf.br/nfe}det")
        
        print(f"\nITENS DA NOTA ({len(itens)}):")
        print("-"*40)
        
        valor_total_itens = 0
        
        for i, item in enumerate(itens, 1):
            prod = item.find("{http://www.portalfiscal.inf.br/nfe}prod")
            if prod is not None:
                codigo = prod.find("{http://www.portalfiscal.inf.br/nfe}cProd")
                descricao = prod.find("{http://www.portalfiscal.inf.br/nfe}xProd")
                ncm = prod.find("{http://www.portalfiscal.inf.br/nfe}NCM")
                cfop = prod.find("{http://www.portalfiscal.inf.br/nfe}CFOP")
                ucom = prod.find("{http://www.portalfiscal.inf.br/nfe}uCom")
                qcom = prod.find("{http://www.portalfiscal.inf.br/nfe}qCom")
                vuncom = prod.find("{http://www.portalfiscal.inf.br/nfe}vUnCom")
                vprod = prod.find("{http://www.portalfiscal.inf.br/nfe}vProd")
                vdesc = prod.find("{http://www.portalfiscal.inf.br/nfe}vDesc")
                
                print(f"\nItem {i}:")
                print(f"  Código: {codigo.text if codigo is not None else 'N/A'}")
                print(f"  Descrição: {descricao.text if descricao is not None else 'N/A'}")
                print(f"  NCM: {ncm.text if ncm is not None else 'N/A'}")
                print(f"  CFOP: {cfop.text if cfop is not None else 'N/A'}")
                
                if qcom is not None and ucom is not None and vuncom is not None:
                    print(f"  Quantidade: {float(qcom.text):.4f} {ucom.text} x R$ {float(vuncom.text):.4f}")
                
                v_prod_valor = float(vprod.text) if vprod is not None else 0
                v_desc_valor = float(vdesc.text) if vdesc is not None and vdesc.text else 0
                v_liquido = v_prod_valor - v_desc_valor
                
                print(f"  Valor bruto: R$ {v_prod_valor:.2f}")
                print(f"  Desconto: R$ {v_desc_valor:.2f}")
                print(f"  Valor líquido: R$ {v_liquido:.2f}")
                
                valor_total_itens += v_liquido
                
                # Impostos
                imposto = item.find("{http://www.portalfiscal.inf.br/nfe}imposto")
                if imposto is not None:
                    # ICMS
                    icms = imposto.find(".//{http://www.portalfiscal.inf.br/nfe}ICMS")
                    if icms is not None:
                        for icms_tipo in icms:
                            origem = icms_tipo.find("{http://www.portalfiscal.inf.br/nfe}orig")
                            cst = icms_tipo.find("{http://www.portalfiscal.inf.br/nfe}CST") or icms_tipo.find("{http://www.portalfiscal.inf.br/nfe}CSOSN")
                            if origem is not None and cst is not None:
                                print(f"  ICMS: Origem {origem.text}, CST/CSOSN {cst.text}")
                    
                    # PIS
                    pis = imposto.find(".//{http://www.portalfiscal.inf.br/nfe}PIS")
                    if pis is not None:
                        for pis_tipo in pis:
                            if pis_tipo.tag.endswith('PISAliq') or pis_tipo.tag.endswith('PISQtde') or pis_tipo.tag.endswith('PISNT') or pis_tipo.tag.endswith('PISOutr'):
                                cst = pis_tipo.find("{http://www.portalfiscal.inf.br/nfe}CST")
                                if cst is not None:
                                    print(f"  PIS: CST {cst.text}")
                    
                    # COFINS
                    cofins = imposto.find(".//{http://www.portalfiscal.inf.br/nfe}COFINS")
                    if cofins is not None:
                        for cofins_tipo in cofins:
                            if cofins_tipo.tag.endswith('COFINSAliq') or cofins_tipo.tag.endswith('COFINSQtde') or cofins_tipo.tag.endswith('COFINSNT') or cofins_tipo.tag.endswith('COFINSOutr'):
                                cst = cofins_tipo.find("{http://www.portalfiscal.inf.br/nfe}CST")
                                if cst is not None:
                                    print(f"  COFINS: CST {cst.text}")
        
        # 5. Análise de consistência
        print("\nANÁLISE DE CONSISTÊNCIA:")
        print("-"*40)
        
        v_nf_valor = float(v_nf.text) if v_nf is not None else 0
        diferenca = abs(valor_total_itens - v_nf_valor)
        
        print(f"Valor total dos itens (líquido): R$ {valor_total_itens:.2f}")
        print(f"Valor total da nota: R$ {v_nf_valor:.2f}")
        print(f"Diferença: R$ {diferenca:.2f} ({diferenca/v_nf_valor*100 if v_nf_valor else 0:.2f}%)")
        
        if diferenca > 0.01:
            print("\nOBSERVAÇÃO: Há diferença significativa entre o somatório dos itens e o valor total da nota.")
            print("Isso pode ser devido a:")
            print("- Arredondamentos")
            print("- Fretes, seguros e outras despesas não discriminadas por item")
            print("- Elementos especiais não contabilizados no somatório dos itens")
        else:
            print("\nConsistência de valores: OK")
        
        # 6. Informações adicionais
        inf_adic = root.find(".//{http://www.portalfiscal.inf.br/nfe}infAdic")
        if inf_adic is not None:
            inf_adic_fisco = inf_adic.find("{http://www.portalfiscal.inf.br/nfe}infAdFisco")
            inf_cpl = inf_adic.find("{http://www.portalfiscal.inf.br/nfe}infCpl")
            
            if inf_adic_fisco is not None or inf_cpl is not None:
                print("\nINFORMAÇÕES ADICIONAIS:")
                print("-"*40)
                
                if inf_adic_fisco is not None:
                    print(f"Informações adicionais de interesse do Fisco: {inf_adic_fisco.text}")
                
                if inf_cpl is not None:
                    print(f"Informações complementares: {inf_cpl.text}")
        
        # 7. Eventos relacionados (protocolo, cancelamento, etc)
        prot_nfe = root.find(".//{http://www.portalfiscal.inf.br/nfe}protNFe")
        eventos = root.findall(".//{http://www.portalfiscal.inf.br/nfe}procEventoNFe")
        
        if prot_nfe is not None or eventos:
            print("\nPROTOCOLO E EVENTOS:")
            print("-"*40)
            
            if prot_nfe is not None:
                inf_prot = prot_nfe.find("{http://www.portalfiscal.inf.br/nfe}infProt")
                if inf_prot is not None:
                    n_prot = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}nProt")
                    dh_recbto = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}dhRecbto")
                    cstat = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}cStat")
                    xmotivo = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}xMotivo")
                    
                    if n_prot is not None:
                        print(f"Protocolo de autorização: {n_prot.text}")
                    
                    if dh_recbto is not None:
                        print(f"Data/hora de recebimento: {dh_recbto.text}")
                    
                    if cstat is not None and xmotivo is not None:
                        print(f"Status do protocolo: {cstat.text} - {xmotivo.text}")
            
            for evento in eventos:
                det_evento = evento.find(".//{http://www.portalfiscal.inf.br/nfe}detEvento")
                if det_evento is not None:
                    desc_evento = det_evento.find("{http://www.portalfiscal.inf.br/nfe}descEvento")
                    if desc_evento is not None:
                        print(f"Evento: {desc_evento.text}")
        
        print("\n" + "="*60)
        print(f"Análise concluída em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return True
    except Exception as e:
        print(f"ERRO ao analisar o XML: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python analisar_xml_detalhado.py <caminho_do_xml>")
        return 1
    
    caminho_xml = sys.argv[1]
    if not analisar_xml(caminho_xml):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())