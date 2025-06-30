#!/usr/bin/env python3
"""
EXTRATOR UNIVERSAL DE PDFs PGDAS
Script genérico para extrair dados de qualquer PDF de PGDAS

USO:
    python3 extrator_universal_pgdas.py [PDF_OU_PASTA] [PASTA_SAIDA]
    
EXEMPLOS:
    python3 extrator_universal_pgdas.py arquivo.pdf
    python3 extrator_universal_pgdas.py pasta_pdfs/ pasta_saida/
    python3 extrator_universal_pgdas.py  (usa pasta atual)
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
import logging

try:
    import pdfplumber
except ImportError:
    print("❌ ERRO: pdfplumber não instalado")
    print("Execute: pip install pdfplumber")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ExtratorPGDASUniversal:
    def __init__(self):
        self.template_base = {
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
                "aliquota_apurada": 0.0,
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
                    "pis": {"declarado": 0.0, "apurado": 0.0, "credito": 0.0},
                    "cofins": {"declarado": 0.0, "apurado": 0.0, "credito": 0.0},
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
        """Extrai texto completo do PDF"""
        try:
            texto = ""
            with pdfplumber.open(caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"
            return texto
        except Exception as e:
            logger.error(f"Erro ao ler PDF {caminho_pdf}: {e}")
            return ""

    def extrair_cnpj(self, texto):
        """Extrai e formata CNPJ"""
        patterns = [
            r'CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})',
            r'(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})',
            r'CNPJ Básico[:\s]*(\d{2}\.?\d{3}\.?\d{3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                cnpj_raw = re.sub(r'[^\d]', '', match.group(1))
                if len(cnpj_raw) >= 8:
                    if len(cnpj_raw) == 8:  # CNPJ básico
                        return f"{cnpj_raw[:2]}.{cnpj_raw[2:5]}.{cnpj_raw[5:8]}/0001-00"
                    else:  # CNPJ completo
                        return f"{cnpj_raw[:2]}.{cnpj_raw[2:5]}.{cnpj_raw[5:8]}/{cnpj_raw[8:12]}-{cnpj_raw[12:14]}"
        return ""

    def extrair_razao_social(self, texto):
        """Extrai razão social"""
        patterns = [
            r'Nome Empresarial[:\s]*([A-ZÀ-Ÿ\s&\-\.]+?)(?:\n|Data|CNPJ|Regime)',
            r'Razão Social[:\s]*([A-ZÀ-Ÿ\s&\-\.]+?)(?:\n|Data|CNPJ)',
            r'CNPJ Básico[:\s]*\d+\.?\d+\.?\d+\s+Nome Empresarial[:\s]*([A-ZÀ-Ÿ\s&\-\.]+?)(?:\n|Data)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return ""

    def extrair_periodo(self, texto):
        """Extrai período de apuração"""
        patterns = [
            r'Período de Apuração[:\s\(PA\)]*[:\s]*(\d{2}/\d{4})',
            r'PA[:\s]*(\d{2}/\d{4})',
            r'apuração[:\s]*(\d{2}/\d{4})',
            r'(\d{2}/\d{4})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, texto, re.IGNORECASE)
            if matches:
                return matches[0]  # Primeiro período encontrado
        return ""

    def extrair_receita_pa(self, texto):
        """Extrai receita bruta do período"""
        patterns = [
            r'Receita Bruta do PA[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'RPA[^0-9]*Competência[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'Competência[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'PA.*?(\d{1,3}(?:\.\d{3})*,\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE | re.DOTALL)
            if match:
                return self.converter_moeda(match.group(1))
        return 0.0

    def extrair_receita_12_meses(self, texto):
        """Extrai receita bruta 12 meses"""
        patterns = [
            r'doze meses anteriores[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'RBT12[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'acumulada.*?(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'12 meses.*?(\d{1,3}(?:\.\d{3})*,\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE | re.DOTALL)
            if match:
                return self.converter_moeda(match.group(1))
        return 0.0

    def extrair_tributos(self, texto):
        """Extrai todos os tributos declarados"""
        tributos = {
            "pis": 0.0, "cofins": 0.0, "icms": 0.0, 
            "irpj": 0.0, "csll": 0.0, "cpp": 0.0, "total": 0.0
        }
        
        # Buscar seção "Total do Débito Exigível"
        secao_total = re.search(
            r'Total do Débito Exigível.*?(?=\n.*?\n|\Z)', 
            texto, re.IGNORECASE | re.DOTALL
        )
        
        if secao_total:
            linha_totais = secao_total.group(0)
            valores = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})', linha_totais)
            
            if len(valores) >= 6:
                tributos["irpj"] = self.converter_moeda(valores[0])
                tributos["csll"] = self.converter_moeda(valores[1])
                tributos["cofins"] = self.converter_moeda(valores[2])
                tributos["pis"] = self.converter_moeda(valores[3])
                tributos["cpp"] = self.converter_moeda(valores[4])
                tributos["icms"] = self.converter_moeda(valores[5])
                if len(valores) >= 9:
                    tributos["total"] = self.converter_moeda(valores[8])
        
        # Busca individual caso não encontrou na seção
        patterns_individuais = {
            "irpj": [r'IRPJ[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "csll": [r'CSLL[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "cofins": [r'COFINS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "pis": [r'PIS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})', r'PIS/PASEP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "cpp": [r'INSS/CPP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})', r'CPP[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})'],
            "icms": [r'ICMS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})']
        }
        
        for tributo, patterns in patterns_individuais.items():
            if tributos[tributo] == 0.0:
                for pattern in patterns:
                    matches = re.findall(pattern, texto, re.IGNORECASE)
                    if matches:
                        tributos[tributo] = self.converter_moeda(matches[-1])
                        break
        
        # Calcular total se não foi encontrado
        if tributos["total"] == 0.0:
            tributos["total"] = sum(v for k, v in tributos.items() if k != "total")
        
        return tributos

    def extrair_valores_monetarios(self, texto):
        """Extrai todos os valores monetários do texto"""
        valores = []
        patterns = [
            r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'(\d{1,3}(?:\.\d{3})*,\d{2})'
        ]
        
        linhas = texto.split('\n')
        for i, linha in enumerate(linhas):
            for pattern in patterns:
                matches = re.findall(pattern, linha)
                for valor in matches:
                    if self.converter_moeda(valor) > 0:
                        valores.append({
                            "linha": f"Linha {i+1}: {linha.strip()[:50]}...",
                            "valor": valor
                        })
                        break  # Apenas primeiro valor por linha
        
        return valores[:20]  # Limitar a 20 valores

    def converter_moeda(self, valor_str):
        """Converte string monetária brasileira para float"""
        if not valor_str:
            return 0.0
        try:
            return float(valor_str.replace('.', '').replace(',', '.'))
        except:
            return 0.0

    def calcular_percentuais_tributos(self, tributos):
        """Calcula percentuais de cada tributo"""
        total = tributos.get("total", 0)
        if total <= 0:
            return {k: 0.0 for k in tributos.keys() if k != "total"}
        
        return {
            k: (v / total) if k != "total" else 0.0 
            for k, v in tributos.items()
        }

    def calcular_creditos(self, tributos):
        """Calcula créditos tributários estimados"""
        return {
            "pis": {
                "declarado": tributos.get("pis", 0.0),
                "apurado": 0.0,  # Seria calculado com dados dos XMLs
                "credito": tributos.get("pis", 0.0)  # Simplificado
            },
            "cofins": {
                "declarado": tributos.get("cofins", 0.0),
                "apurado": 0.0,
                "credito": tributos.get("cofins", 0.0)
            },
            "total_credito": tributos.get("pis", 0.0) + tributos.get("cofins", 0.0),
            "credito_atualizado": (tributos.get("pis", 0.0) + tributos.get("cofins", 0.0)) * 1.04
        }

    def calcular_aliquota_apurada(self, rbt12):
        """Calcula a alíquota apurada usando a tabela do Anexo do Simples Nacional"""
        import json
        tabela_path = os.path.join(os.path.dirname(__file__), '../src/core/data/tabelas/Anexo do Simples.json')
        with open(tabela_path, encoding='utf-8') as f:
            tabela = json.load(f)
        faixa = None
        aliquota_nominal = 0.0
        valor_deduzir = 0.0
        # Encontrar faixa correta
        for linha in tabela:
            if not linha or not isinstance(linha, dict):
                continue
            faixa_nome = linha.get('Anexo I', '')
            faixa_valor = linha.get('Column2', '')
            if 'Até' in faixa_valor:
                limite = float(faixa_valor.replace('Até','').replace('.','').replace(',','.').strip())
                if rbt12 <= limite:
                    aliquota_nominal = float(linha['Column3'])
                    valor_deduzir = 0.0 if linha['Column4'] == '-' else float(linha['Column4'])
                    break
            elif 'a' in faixa_valor:
                partes = faixa_valor.replace('De','').split('a')
                min_ = float(partes[0].replace('.','').replace(',','.').strip())
                max_ = float(partes[1].replace('.','').replace(',','.').strip())
                if min_ < rbt12 <= max_:
                    aliquota_nominal = float(linha['Column3'])
                    valor_deduzir = float(linha['Column4'])
                    break
        if aliquota_nominal == 0.0:
            return 0.0
        return ((rbt12 * aliquota_nominal) - valor_deduzir) / rbt12

    def processar_pdf(self, caminho_pdf):
        """Processa um único PDF"""
        logger.info(f"Processando: {os.path.basename(caminho_pdf)}")
        
        # Extrair texto
        texto = self.extrair_texto_pdf(caminho_pdf)
        if not texto:
            logger.error(f"Não foi possível extrair texto de {caminho_pdf}")
            return None
        
        # Criar estrutura de dados
        dados = json.loads(json.dumps(self.template_base))
        dados["arquivo_origem"] = os.path.basename(caminho_pdf)
        dados["data_processamento"] = datetime.now().isoformat()
        dados["conteudo_extraido"] = texto[:1000] + "..." if len(texto) > 1000 else texto
        
        # Extrair dados específicos
        estruturados = dados["dados_estruturados"]
        estruturados["cnpj"] = self.extrair_cnpj(texto)
        estruturados["razao_social"] = self.extrair_razao_social(texto)
        estruturados["periodo_apuracao"] = self.extrair_periodo(texto)
        estruturados["receita_bruta_pa"] = self.extrair_receita_pa(texto)
        estruturados["receita_bruta_12_meses"] = self.extrair_receita_12_meses(texto)
        # NOVO: calcular aliquota_apurada
        estruturados["aliquota_apurada"] = self.calcular_aliquota_apurada(estruturados["receita_bruta_12_meses"])
        
        # Atualizar período no nível raiz
        dados["periodo_apuracao"] = estruturados["periodo_apuracao"]
        
        # Extrair tributos
        tributos = self.extrair_tributos(texto)
        estruturados["tributos_declarados"] = tributos
        
        # Calcular percentuais
        estruturados["percentuais_tributos"] = self.calcular_percentuais_tributos(tributos)
        
        # Calcular créditos
        estruturados["creditos_apurados"] = self.calcular_creditos(tributos)
        
        # Extrair valores
        estruturados["valores"] = self.extrair_valores_monetarios(texto)
        
        # Log de resultado
        logger.info(f"✅ Sucesso: {os.path.basename(caminho_pdf)}")
        logger.info(f"   CNPJ: {estruturados['cnpj'] or 'Não encontrado'}")
        logger.info(f"   Período: {estruturados['periodo_apuracao'] or 'Não encontrado'}")
        logger.info(f"   Receita PA: R$ {estruturados['receita_bruta_pa']:,.2f}")
        logger.info(f"   Total Tributos: R$ {tributos['total']:,.2f}")
        
        return dados

    def processar_arquivo_ou_pasta(self, entrada, saida=None):
        """Processa um arquivo PDF ou pasta com PDFs"""
        if not os.path.exists(entrada):
            logger.error(f"Caminho não existe: {entrada}")
            return False
        
        # Determinar pasta de saída
        if saida is None:
            if os.path.isfile(entrada):
                saida = os.path.dirname(entrada) or "."
            else:
                saida = entrada
        
        # Encontrar PDFs
        if os.path.isfile(entrada) and entrada.lower().endswith('.pdf'):
            pdfs = [entrada]
        else:
            pdfs = []
            for root, dirs, files in os.walk(entrada):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdfs.append(os.path.join(root, file))
        
        if not pdfs:
            logger.warning("Nenhum PDF encontrado!")
            return False
        
        logger.info(f"🚀 Processando {len(pdfs)} PDFs...")
        
        sucessos = 0
        erros = 0
        
        for pdf in pdfs:
            try:
                dados = self.processar_pdf(pdf)
                if dados:
                    periodo = dados["dados_estruturados"].get("periodo_apuracao") or "SEM_PERIODO"
                    periodo = periodo.replace("/", "-")
                    saida_periodo = os.path.join(saida, periodo)
                    os.makedirs(saida_periodo, exist_ok=True)
                    nome_json = os.path.splitext(os.path.basename(pdf))[0] + ".json"
                    caminho_json = os.path.join(saida_periodo, nome_json)
                    with open(caminho_json, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, indent=2, ensure_ascii=False)
                    logger.info(f"💾 Salvo: {os.path.join(periodo, nome_json)}")
                    sucessos += 1
                else:
                    erros += 1
            except Exception as e:
                logger.error(f"❌ Erro em {os.path.basename(pdf)}: {e}")
                erros += 1
        
        logger.info(f"\n📊 RESULTADO FINAL:")
        logger.info(f"   ✅ Sucessos: {sucessos}")
        logger.info(f"   ❌ Erros: {erros}")
        logger.info(f"   📁 JSONs salvos em: {saida}")
        
        return sucessos > 0


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Extrator Universal de PDFs PGDAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:
    %(prog)s arquivo.pdf
    %(prog)s pasta_pdfs/
    %(prog)s arquivo.pdf pasta_saida/
    %(prog)s pasta_pdfs/ pasta_resultados/
    %(prog)s  (usa pasta atual)
        """
    )
    
    parser.add_argument(
        'entrada', 
        nargs='?', 
        default='.', 
        help='Arquivo PDF ou pasta com PDFs (padrão: pasta atual)'
    )
    parser.add_argument(
        'saida', 
        nargs='?', 
        help='Pasta de saída (padrão: criar subpasta no local de entrada)'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Modo verboso'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🔄 EXTRATOR UNIVERSAL DE PDFs PGDAS")
    print("=" * 50)
    
    extrator = ExtratorPGDASUniversal()
    sucesso = extrator.processar_arquivo_ou_pasta(args.entrada, args.saida)
    
    if sucesso:
        print("\n🎉 Processamento concluído com sucesso!")
    else:
        print("\n❌ Falha no processamento!")
        sys.exit(1)


if __name__ == "__main__":
    main()
