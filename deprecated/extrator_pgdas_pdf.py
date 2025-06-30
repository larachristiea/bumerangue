#!/usr/bin/env python3
"""
EXTRATOR AUTOMÁTICO DE PDFs PGDAS
Extrai dados estruturados de PDFs de PGDAS e gera JSONs padronizados
"""

import os
import json
import re
import pdfplumber
from datetime import datetime
from decimal import Decimal
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExtratorPGDAS:
    def __init__(self):
        self.template_json = {
            "arquivo_origem": "",
            "data_processamento": "",
            "periodo_apuracao": "",
            "conteudo_extraido": "",
            "dados_estruturados": {
                "cnpj": "",
                "razao_social": "",
                "periodo_apuracao": "",
                "receita_bruta_pa": 0.0,
                "receita_bruta_12_meses": 0.0,
                "faixa_tributacao": 0,
                "aliquota_nominal": 0.0,
                "valor_deduzir": 0.0,
                "aliquota_efetiva": 0.0,
                "tributos_declarados": {
                    "pis": 0.0,
                    "cofins": 0.0,
                    "icms": 0.0,
                    "irpj": 0.0,
                    "csll": 0.0,
                    "cpp": 0.0,
                    "total": 0.0
                },
                "percentuais_tributos": {
                    "pis": 0.0,
                    "cofins": 0.0,
                    "icms": 0.0,
                    "irpj": 0.0,
                    "csll": 0.0,
                    "cpp": 0.0
                },
                "dados_classificacao": {
                    "receita_bruta_vendas": 0.0,
                    "receita_sem_descontos": 0.0,
                    "receita_monofasicos": 0.0,
                    "receita_nao_monofasicos": 0.0,
                    "total_itens_monofasicos": 0,
                    "total_itens_nao_monofasicos": 0,
                    "proporcao_monofasicos": 0.0
                },
                "creditos_apurados": {
                    "pis": {
                        "declarado": 0.0,
                        "apurado": 0.0,
                        "credito": 0.0
                    },
                    "cofins": {
                        "declarado": 0.0,
                        "apurado": 0.0,
                        "credito": 0.0
                    },
                    "total_credito": 0.0,
                    "credito_atualizado": 0.0
                },
                "estatisticas": {
                    "total_xmls": 0,
                    "xmls_processados": 0
                },
                "valores": []
            }
        }

    def extrair_texto_pdf(self, caminho_pdf):
        """Extrai todo o texto do PDF"""
        try:
            texto_completo = ""
            with pdfplumber.open(caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
            return texto_completo
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {caminho_pdf}: {str(e)}")
            return ""

    def extrair_cnpj(self, texto):
        """Extrai CNPJ do texto"""
        patterns = [
            r'CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})',
            r'(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})',
            r'CNPJ Básico[:\s]*(\d{2}\.?\d{3}\.?\d{3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                cnpj = match.group(1)
                # Padronizar formato
                cnpj_numeros = re.sub(r'[^\d]', '', cnpj)
                if len(cnpj_numeros) >= 8:
                    if len(cnpj_numeros) == 8:  # CNPJ básico
                        return f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/0001-65"
                    else:  # CNPJ completo
                        return f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:14]}"
        return ""
    def extrair_razao_social(self, texto):
        """Extrai razão social do texto"""
        patterns = [
            r'Nome Empresarial[:\s]*([A-Z\s&]+?)(?:\n|Data|CNPJ)',
            r'Razão Social[:\s]*([A-Z\s&]+?)(?:\n|Data|CNPJ)',
            r'CNPJ Básico[:\s]*\d+\.?\d+\.?\d+\s+Nome Empresarial[:\s]*([A-Z\s&]+?)(?:\n|Data)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def extrair_periodo_apuracao(self, texto):
        """Extrai período de apuração"""
        patterns = [
            r'Período de Apuração[:\s\(PA\)]*[:\s]*(\d{2}/\d{4})',
            r'PA[:\s]*(\d{2}/\d{4})',
            r'(\d{2}/\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                return match.group(1)
        return ""

    def extrair_receita_bruta_pa(self, texto):
        """Extrai receita bruta do período de apuração"""
        patterns = [
            r'Receita Bruta do PA[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'RPA[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'Competência[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                return self.converter_valor_monetario(match.group(1))
        return 0.0

    def extrair_receita_bruta_12_meses(self, texto):
        """Extrai receita bruta acumulada 12 meses"""
        patterns = [
            r'doze meses anteriores[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'RBT12[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'acumulada[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                return self.converter_valor_monetario(match.group(1))
        return 0.0

    def extrair_tributos_declarados(self, texto):
        """Extrai valores dos tributos declarados"""
        tributos = {
            "pis": 0.0,
            "cofins": 0.0,
            "icms": 0.0,
            "irpj": 0.0,
            "csll": 0.0,
            "cpp": 0.0,
            "total": 0.0
        }
        
        # Patterns para cada tributo
        patterns = {
            "irpj": [r'IRPJ[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "csll": [r'CSLL[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "cofins": [r'COFINS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "pis": [r'PIS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})', r'PIS/PASEP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "cpp": [r'INSS/CPP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})', r'CPP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "icms": [r'ICMS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})']
        }
        
        # Buscar seção "Total do Débito Exigível"
        secao_debito = re.search(r'Total do Débito Exigível.*?(\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+.*?\d+,\d+)', texto, re.DOTALL)
        
        if secao_debito:
            linha_valores = secao_debito.group(1)
            valores = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})', linha_valores)
            
            if len(valores) >= 6:
                tributos["irpj"] = self.converter_valor_monetario(valores[0])
                tributos["csll"] = self.converter_valor_monetario(valores[1])
                tributos["cofins"] = self.converter_valor_monetario(valores[2])
                tributos["pis"] = self.converter_valor_monetario(valores[3])
                tributos["cpp"] = self.converter_valor_monetario(valores[4])
                tributos["icms"] = self.converter_valor_monetario(valores[5])
                if len(valores) >= 9:
                    tributos["total"] = self.converter_valor_monetario(valores[8])
        
        # Se não encontrou na seção, buscar individualmente
        for tributo, patterns_list in patterns.items():
            if tributos[tributo] == 0.0:
                for pattern in patterns_list:
                    matches = re.findall(pattern, texto, re.IGNORECASE)
                    if matches:
                        # Pegar o último valor encontrado (geralmente o total)
                        tributos[tributo] = self.converter_valor_monetario(matches[-1])
                        break
        
        # Calcular total se não foi encontrado
        if tributos["total"] == 0.0:
            tributos["total"] = sum([v for k, v in tributos.items() if k != "total"])
        
        return tributos

    def extrair_valores_linha(self, texto):
        """Extrai todos os valores monetários encontrados no texto"""
        valores = []
        
        # Buscar todas as linhas com valores monetários
        linhas_com_valores = re.findall(r'.*?R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2}).*', texto)
        
        for i, valor in enumerate(linhas_com_valores):
            valores.append({
                "linha": f"Valor encontrado {i+1}: R$ {valor}",
                "valor": valor
            })
        
        return valores

    def converter_valor_monetario(self, valor_str):
        """Converte string monetária para float"""
        if not valor_str:
            return 0.0
        
        try:
            # Remove pontos dos milhares e converte vírgula para ponto
            valor_limpo = valor_str.replace('.', '').replace(',', '.')
            return float(valor_limpo)
        except (ValueError, AttributeError):
            return 0.0

    def calcular_creditos_apurados(self, tributos_declarados, dados_classificacao):
        """Calcula créditos tributários baseado nos dados processados"""
        creditos = {
            "pis": {
                "declarado": tributos_declarados.get("pis", 0.0),
                "apurado": 0.0,
                "credito": 0.0
            },
            "cofins": {
                "declarado": tributos_declarados.get("cofins", 0.0),
                "apurado": 0.0,
                "credito": 0.0
            },
            "total_credito": 0.0,
            "credito_atualizado": 0.0
        }
        
        # Se houver dados de classificação, calcular valores apurados
        if dados_classificacao.get("receita_nao_monofasicos", 0) > 0:
            # Calcular alíquotas médias baseadas nos tributos declarados
            receita_total = dados_classificacao.get("receita_monofasicos", 0) + dados_classificacao.get("receita_nao_monofasicos", 0)
            
            if receita_total > 0:
                aliquota_pis = tributos_declarados.get("pis", 0) / receita_total
                aliquota_cofins = tributos_declarados.get("cofins", 0) / receita_total
                
                # Calcular valores apurados (apenas sobre não-monofásicos)
                creditos["pis"]["apurado"] = dados_classificacao.get("receita_nao_monofasicos", 0) * aliquota_pis
                creditos["cofins"]["apurado"] = dados_classificacao.get("receita_nao_monofasicos", 0) * aliquota_cofins
        
        # Calcular créditos (declarado - apurado)
        creditos["pis"]["credito"] = creditos["pis"]["declarado"] - creditos["pis"]["apurado"]
        creditos["cofins"]["credito"] = creditos["cofins"]["declarado"] - creditos["cofins"]["apurado"]
        creditos["total_credito"] = creditos["pis"]["credito"] + creditos["cofins"]["credito"]
        
        # Atualização com SELIC (por simplicidade, usar fator 1.04)
        creditos["credito_atualizado"] = creditos["total_credito"] * 1.04
        
        return creditos

    def processar_pdf(self, caminho_pdf):
        """Processa um único PDF e retorna dados estruturados"""
        logger.info(f"Processando: {os.path.basename(caminho_pdf)}")
        
        # Extrair texto do PDF
        texto = self.extrair_texto_pdf(caminho_pdf)
        if not texto:
            logger.error(f"Não foi possível extrair texto de {caminho_pdf}")
            return None
        
        # Criar estrutura baseada no template
        dados = json.loads(json.dumps(self.template_json))
        
        # Preencher metadados
        dados["arquivo_origem"] = os.path.basename(caminho_pdf)
        dados["data_processamento"] = datetime.now().isoformat()
        dados["conteudo_extraido"] = texto[:1000] + "..." if len(texto) > 1000 else texto
        
        # Extrair dados específicos
        dados["dados_estruturados"]["cnpj"] = self.extrair_cnpj(texto)
        dados["dados_estruturados"]["razao_social"] = self.extrair_razao_social(texto)
        dados["dados_estruturados"]["periodo_apuracao"] = self.extrair_periodo_apuracao(texto)
        dados["periodo_apuracao"] = dados["dados_estruturados"]["periodo_apuracao"]
        
        dados["dados_estruturados"]["receita_bruta_pa"] = self.extrair_receita_bruta_pa(texto)
        dados["dados_estruturados"]["receita_bruta_12_meses"] = self.extrair_receita_bruta_12_meses(texto)
        
        # Extrair tributos
        tributos = self.extrair_tributos_declarados(texto)
        dados["dados_estruturados"]["tributos_declarados"] = tributos
        
        # Calcular percentuais dos tributos
        total_tributos = tributos.get("total", 0)
        if total_tributos > 0:
            for tributo, valor in tributos.items():
                if tributo != "total":
                    dados["dados_estruturados"]["percentuais_tributos"][tributo] = valor / total_tributos
        
        # Calcular créditos (baseado nos dados extraídos)
        dados["dados_estruturados"]["creditos_apurados"] = self.calcular_creditos_apurados(
            tributos, 
            dados["dados_estruturados"]["dados_classificacao"]
        )
        
        # Extrair valores para lista
        dados["dados_estruturados"]["valores"] = self.extrair_valores_linha(texto)
        
        logger.info(f"✅ Processado com sucesso: {os.path.basename(caminho_pdf)}")
        logger.info(f"   CNPJ: {dados['dados_estruturados']['cnpj']}")
        logger.info(f"   Período: {dados['dados_estruturados']['periodo_apuracao']}")
        logger.info(f"   Receita PA: R$ {dados['dados_estruturados']['receita_bruta_pa']:.2f}")
        logger.info(f"   Total Tributos: R$ {tributos.get('total', 0):.2f}")
        
        return dados

    def processar_diretorio(self, diretorio_pdfs, diretorio_saida):
        """Processa todos os PDFs de um diretório"""
        if not os.path.exists(diretorio_pdfs):
            logger.error(f"Diretório não encontrado: {diretorio_pdfs}")
            return
        
        # Criar diretório de saída se não existir
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Listar todos os PDFs
        pdfs = [f for f in os.listdir(diretorio_pdfs) if f.lower().endswith('.pdf')]
        
        if not pdfs:
            logger.warning(f"Nenhum PDF encontrado em: {diretorio_pdfs}")
            return
        
        logger.info(f"🚀 Iniciando processamento de {len(pdfs)} PDFs...")
        
        sucessos = 0
        erros = 0
        
        for pdf in pdfs:
            try:
                caminho_pdf = os.path.join(diretorio_pdfs, pdf)
                dados = self.processar_pdf(caminho_pdf)
                
                if dados:
                    # Gerar nome do arquivo JSON baseado no PDF
                    nome_json = pdf.replace('.pdf', '.json')
                    caminho_json = os.path.join(diretorio_saida, nome_json)
                    
                    # Salvar JSON
                    with open(caminho_json, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"💾 Salvo: {nome_json}")
                    sucessos += 1
                else:
                    logger.error(f"❌ Falha ao processar: {pdf}")
                    erros += 1
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar {pdf}: {str(e)}")
                erros += 1
        
        logger.info(f"\n📊 RELATÓRIO FINAL:")
        logger.info(f"   ✅ Sucessos: {sucessos}")
        logger.info(f"   ❌ Erros: {erros}")
        logger.info(f"   📁 JSONs salvos em: {diretorio_saida}")


def main():
    """Função principal"""
    print("🔄 EXTRATOR AUTOMÁTICO DE PDFs PGDAS")
    print("=" * 50)
    
    # Configurar caminhos
    DIRETORIO_BASE = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/src/core/data/pgdas"
    DIRETORIO_PDFS_2022 = os.path.join(DIRETORIO_BASE, "PGDAS 2022 PDF")
    DIRETORIO_PDFS_2023 = os.path.join(DIRETORIO_BASE, "PGDAS 2023 PDF")
    DIRETORIO_SAIDA = os.path.join(DIRETORIO_BASE, "JSON_EXTRAIDOS")
    
    # Criar extrator
    extrator = ExtratorPGDAS()
    
    # Processar PDFs de 2022
    if os.path.exists(DIRETORIO_PDFS_2022):
        print(f"\n📂 Processando PDFs de 2022...")
        saida_2022 = os.path.join(DIRETORIO_SAIDA, "2022")
        extrator.processar_diretorio(DIRETORIO_PDFS_2022, saida_2022)
    
    # Processar PDFs de 2023
    if os.path.exists(DIRETORIO_PDFS_2023):
        print(f"\n📂 Processando PDFs de 2023...")
        saida_2023 = os.path.join(DIRETORIO_SAIDA, "2023")
        extrator.processar_diretorio(DIRETORIO_PDFS_2023, saida_2023)
    
    # Processar PDFs avulsos na pasta raiz
    pdfs_raiz = [f for f in os.listdir(DIRETORIO_BASE) if f.lower().endswith('.pdf')]
    if pdfs_raiz:
        print(f"\n📂 Processando PDFs avulsos...")
        saida_avulsos = os.path.join(DIRETORIO_SAIDA, "avulsos")
        extrator.processar_diretorio(DIRETORIO_BASE, saida_avulsos)
    
    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"📁 Verifique os JSONs em: {DIRETORIO_SAIDA}")


if __name__ == "__main__":
    main()
