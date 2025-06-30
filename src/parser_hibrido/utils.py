#!/usr/bin/env python3
"""
Utilitários para Parser de NFe
Funções auxiliares para processamento de XML e dados fiscais
"""

import os
import re
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, Union, List, Dict, Any
from lxml import etree

# Configurar logging
logger = logging.getLogger(__name__)

# Namespace padrão para NFe
NAMESPACE_NFE = {
    'nfe': 'http://www.portalfiscal.inf.br/nfe'
}

class UtilXML:
    """Utilitários para manipulação de XML de NFe"""
    
    @staticmethod
    def encontrar_elemento(elemento, tag_name: str, namespace: Dict[str, str] = None) -> Optional[etree.Element]:
        """
        Encontra elemento no XML com suporte a namespace
        Abordagem híbrida: tenta com namespace explícito, depois flexível
        """
        if elemento is None:
            return None
        
        # Tentar com namespace explícito primeiro
        if namespace:
            try:
                resultado = elemento.find(f"nfe:{tag_name}", namespace)
                if resultado is not None:
                    return resultado
            except Exception:
                pass
        
        # Abordagem flexível: buscar por endswith (método da pasta original)
        for child in elemento.iter():
            if child.tag.endswith(tag_name):
                return child
        
        return None
    
    @staticmethod
    def encontrar_todos_elementos(elemento, tag_name: str, namespace: Dict[str, str] = None) -> List[etree.Element]:
        """
        Encontra todos os elementos com tag específica
        """
        if elemento is None:
            return []
        
        resultados = []
        
        # Tentar com namespace explícito primeiro
        if namespace:
            try:
                resultados = elemento.findall(f"nfe:{tag_name}", namespace)
                if resultados:
                    return resultados
            except Exception:
                pass
        
        # Abordagem flexível
        for child in elemento.iter():
            if child.tag.endswith(tag_name):
                resultados.append(child)
        
        return resultados
    
    @staticmethod
    def obter_texto_elemento(elemento, tag_name: str, default: str = "", namespace: Dict[str, str] = None) -> str:
        """
        Obtém texto de um elemento com valor padrão
        """
        encontrado = UtilXML.encontrar_elemento(elemento, tag_name, namespace)
        if encontrado is not None and encontrado.text:
            return encontrado.text.strip()
        return default
    
    @staticmethod
    def extrair_campo_seguro(elemento, xpath: str, tipo_esperado=str, obrigatorio: bool = False, 
                           namespace: Dict[str, str] = None) -> Optional[Union[str, int, float, Decimal]]:
        """
        Extração segura de campo com validação de tipo (adaptado do parser fornecido)
        """
        try:
            # Usar namespace se fornecido
            if namespace and not xpath.startswith('./'):
                valor = elemento.find(xpath, namespace)
            else:
                # Abordagem flexível para xpath sem namespace
                tag_name = xpath.split('/')[-1].replace('nfe:', '')
                valor = UtilXML.encontrar_elemento(elemento, tag_name, namespace)
            
            if valor is None or valor.text is None or valor.text.strip() == '':
                if obrigatorio:
                    logger.error(f"Campo obrigatório {xpath} não encontrado")
                    return None
                else:
                    logger.debug(f"Campo opcional {xpath} não encontrado")
                    return None
            
            texto = valor.text.strip()
            
            # Conversão segura de tipos
            if tipo_esperado == float or tipo_esperado == Decimal:
                # Tratar vírgula como separador decimal
                texto_num = texto.replace(',', '.')
                if not re.match(r'^\d+\.?\d*$', texto_num):
                    logger.warning(f"Valor numérico inválido em {xpath}: {texto}")
                    return None
                return Decimal(texto_num) if tipo_esperado == Decimal else float(texto_num)
            
            elif tipo_esperado == int:
                if not texto.isdigit():
                    logger.warning(f"Valor inteiro inválido em {xpath}: {texto}")
                    return None
                return int(texto)
            
            elif tipo_esperado == str:
                return texto
                
        except Exception as e:
            logger.error(f"Erro ao extrair {xpath}: {e}")
            return None
    
    @staticmethod
    def validar_estrutura_xml(xml_content: Union[str, bytes]) -> bool:
        """
        Validação básica da estrutura XML (adaptado do parser fornecido)
        """
        try:
            # Verificar se é XML bem formado
            if isinstance(xml_content, str):
                xml_content = xml_content.encode('utf-8')
            
            root = etree.fromstring(xml_content)
            
            # Verificar se é NFe ou nfeProc
            tags_validas = [
                '{http://www.portalfiscal.inf.br/nfe}NFe',
                '{http://www.portalfiscal.inf.br/nfe}nfeProc'
            ]
            
            if root.tag not in tags_validas:
                logger.error(f"Tag raiz inválida: {root.tag}")
                return False
                
            return True
            
        except etree.XMLSyntaxError as e:
            logger.error(f"Erro de sintaxe XML: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False

class UtilData:
    """Utilitários para manipulação de datas"""
    
    @staticmethod
    def parsear_data_nfe(data_str: str) -> Optional[datetime]:
        """
        Parseia data de NFe no formato ISO
        """
        if not data_str:
            return None
        
        try:
            # Formato padrão NFe: 2024-12-01T08:29:12-03:00
            if 'T' in data_str:
                data_str = data_str.split('T')[0]  # Pegar apenas a data
            
            return datetime.strptime(data_str, '%Y-%m-%d')
        except ValueError as e:
            logger.warning(f"Erro ao parsear data {data_str}: {e}")
            return None
    
    @staticmethod
    def formatar_data_brasileira(data: datetime) -> str:
        """
        Formata data no padrão brasileiro DD/MM/AAAA
        """
        if not data:
            return ""
        
        return data.strftime('%d/%m/%Y')

class UtilValor:
    """Utilitários para manipulação de valores monetários"""
    
    @staticmethod
    def converter_para_decimal(valor: Any) -> Decimal:
        """
        Converte valor para Decimal com tratamento seguro
        """
        if valor is None or valor == "":
            return Decimal('0')
        
        try:
            # Se já é Decimal, retorna
            if isinstance(valor, Decimal):
                return valor
            
            # Converte string, tratando vírgula como separador decimal
            if isinstance(valor, str):
                valor_limpo = valor.strip().replace(',', '.')
                return Decimal(valor_limpo)
            
            # Converte número
            return Decimal(str(valor))
        
        except (ValueError, TypeError, ArithmeticError):
            logger.warning(f"Erro ao converter valor para Decimal: {valor}")
            return Decimal('0')
    
    @staticmethod
    def formatar_valor_brasileiro(valor: Decimal) -> str:
        """
        Formata valor no padrão brasileiro com vírgula decimal
        """
        if valor is None:
            return "0,00"
        
        return f"{float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

class UtilArquivo:
    """Utilitários para manipulação de arquivos"""
    
    @staticmethod
    def listar_xmls_diretorio(diretorio: str) -> List[str]:
        """
        Lista todos os arquivos XML em um diretório
        """
        if not os.path.exists(diretorio):
            logger.error(f"Diretório não existe: {diretorio}")
            return []
        
        arquivos_xml = []
        for arquivo in os.listdir(diretorio):
            if arquivo.lower().endswith('.xml'):
                caminho_completo = os.path.join(diretorio, arquivo)
                arquivos_xml.append(caminho_completo)
        
        logger.info(f"Encontrados {len(arquivos_xml)} arquivos XML em {diretorio}")
        return arquivos_xml
    
    @staticmethod
    def determinar_tipo_xml(root: etree.Element) -> str:
        """
        Determina o tipo de arquivo XML: nota fiscal ou evento
        """
        # Verificar se é um procEventoNFe (evento)
        if UtilXML.encontrar_elemento(root, 'procEventoNFe') is not None or root.tag.endswith('procEventoNFe'):
            return 'EVENTO'
        
        # Verificar se é um NFe ou procNFe (nota fiscal)
        if (UtilXML.encontrar_elemento(root, 'NFe') is not None or 
            UtilXML.encontrar_elemento(root, 'nfeProc') is not None or
            root.tag.endswith('NFe') or 
            root.tag.endswith('nfeProc')):
            return 'NFE'
        
        return 'DESCONHECIDO'
    
    @staticmethod
    def ler_arquivo_xml(caminho_arquivo: str) -> Optional[str]:
        """
        Lê arquivo XML com tratamento de encoding
        """
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(caminho_arquivo, 'r', encoding=encoding) as f:
                        conteudo = f.read()
                        logger.debug(f"Arquivo {caminho_arquivo} lido com encoding {encoding}")
                        return conteudo
                except UnicodeDecodeError:
                    continue
            
            logger.error(f"Não foi possível ler o arquivo {caminho_arquivo} com nenhum encoding")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {caminho_arquivo}: {e}")
            return None

class UtilTributario:
    """Utilitários para cálculos tributários"""
    
    # CSTs que indicam produtos monofásicos
    CSTS_MONOFASICOS = ['04', '05', '06']
    
    # CSTs válidos para PIS/COFINS
    CSTS_VALIDOS = [
        '01', '02', '03', '04', '05', '06', '07', '08', '09',
        '49', '50', '51', '52', '53', '54', '55', '56',
        '60', '61', '62', '63', '64', '65', '66', '67',
        '70', '71', '72', '73', '74', '75', '98', '99'
    ]
    
    @staticmethod
    def eh_produto_monofasico_por_cst(pis_cst: str, cofins_cst: str) -> bool:
        """
        Verifica se produto é monofásico baseado nos CSTs de PIS/COFINS
        """
        return (pis_cst in UtilTributario.CSTS_MONOFASICOS or 
                cofins_cst in UtilTributario.CSTS_MONOFASICOS)
    
    @staticmethod
    def calcular_aliquotas_efetivas(aliquota_efetiva: Decimal, proporcoes: Dict[str, float]) -> tuple:
        """
        Calcula alíquotas efetivas de PIS e COFINS
        """
        aliquota_pis = aliquota_efetiva * Decimal(str(proporcoes.get("pis", 0.0276)))
        aliquota_cofins = aliquota_efetiva * Decimal(str(proporcoes.get("cofins", 0.1274)))
        
        return aliquota_pis, aliquota_cofins
    
    @staticmethod
    def calcular_proporcao_monofasicos(valor_monofasico: Decimal, valor_total: Decimal) -> Decimal:
        """
        Calcula proporção de produtos monofásicos
        """
        if valor_total == 0:
            return Decimal('0')
        
        return (valor_monofasico / valor_total) * 100

class UtilLog:
    """Utilitários para logging estruturado"""
    
    @staticmethod
    def configurar_logging(nivel: str = "INFO", arquivo_log: Optional[str] = None):
        """
        Configura logging estruturado
        """
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if arquivo_log:
            logging.basicConfig(
                level=getattr(logging, nivel.upper()),
                format=format_str,
                handlers=[
                    logging.FileHandler(arquivo_log, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=getattr(logging, nivel.upper()),
                format=format_str
            )
    
    @staticmethod
    def criar_logger(nome: str) -> logging.Logger:
        """
        Cria logger específico para um módulo
        """
        return logging.getLogger(nome)

def extrair_chave_acesso(elemento_infnfe) -> Optional[str]:
    """
    Extração da chave de acesso do atributo Id (do parser fornecido)
    """
    try:
        id_attr = elemento_infnfe.get('Id')
        if id_attr and id_attr.startswith('NFe'):
            chave = id_attr[3:]  # Remove 'NFe' do início
            if len(chave) == 44 and chave.isdigit():
                return chave
        logger.warning(f"Chave de acesso inválida: {id_attr}")
        return None
    except Exception as e:
        logger.error(f"Erro ao extrair chave de acesso: {e}")
        return None

def detectar_encoding_arquivo(caminho_arquivo: str) -> str:
    """
    Detecta encoding de arquivo automaticamente
    """
    try:
        import chardet
        
        with open(caminho_arquivo, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'] if result['encoding'] else 'utf-8'
    except ImportError:
        logger.warning("Biblioteca chardet não disponível, usando utf-8 como padrão")
        return 'utf-8'
    except Exception as e:
        logger.warning(f"Erro ao detectar encoding: {e}")
        return 'utf-8'

def normalizar_string(texto: str) -> str:
    """
    Normaliza string removendo acentos e caracteres especiais
    """
    if not texto:
        return ""
    
    import unicodedata
    
    # Remove acentos
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_normalizado = ''.join(char for char in texto_normalizado 
                               if unicodedata.category(char) != 'Mn')
    
    return texto_normalizado.strip()

def formatar_cnpj_cpf(documento: str) -> str:
    """
    Formata CNPJ ou CPF com máscara
    """
    if not documento:
        return ""
    
    # Remove formatação existente
    numeros = re.sub(r'\D', '', documento)
    
    if len(numeros) == 11:  # CPF
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    elif len(numeros) == 14:  # CNPJ
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    else:
        return documento  # Retorna original se não for CPF nem CNPJ
