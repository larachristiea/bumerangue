#!/usr/bin/env python3
"""
Parser Híbrido de NFe
Módulo que combina robustez técnica com funcionalidades completas de negócio
"""

from parser_hibrido.parser_hibrido import NFEParserHibrido, processar_xml_nfe_hibrido, processar_diretorio_nfe_hibrido
from parser_hibrido.models import NotaFiscal, ItemNotaFiscal, EventoCancelamento, converter_para_decimal
from parser_hibrido.validators import ValidadorFiscal
from parser_hibrido.utils import (
    UtilXML, UtilData, UtilValor, UtilArquivo, UtilTributario, UtilLog,
    NAMESPACE_NFE, extrair_chave_acesso, formatar_cnpj_cpf
)

def configurar_logging(nivel="INFO", arquivo_log=None):
    """
    Configura logging para o módulo
    
    Args:
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        arquivo_log: Caminho para arquivo de log (opcional)
    """
    UtilLog.configurar_logging(nivel, arquivo_log)

def versao():
    """Retorna versão do módulo"""
    return __version__

__version__ = "1.0.0"
__author__ = "Sistema Híbrido NFe"

# Exportações principais
__all__ = [
    # Classes principais
    'NFEParserHibrido',
    'NotaFiscal',
    'ItemNotaFiscal', 
    'EventoCancelamento',
    'ValidadorFiscal',
    
    # Funções de conveniência
    'processar_xml_nfe_hibrido',
    'processar_diretorio_nfe_hibrido',
    'converter_para_decimal',
    
    # Utilitários
    'UtilXML',
    'UtilData',
    'UtilValor',
    'UtilArquivo',
    'UtilTributario',
    'UtilLog',
    
    # Constantes
    'NAMESPACE_NFE',
    
    # Funções auxiliares
    'extrair_chave_acesso',
    'formatar_cnpj_cpf'
]

def configurar_logging(nivel="INFO", arquivo_log=None):
    """
    Configura logging para o módulo
    
    Args:
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        arquivo_log: Caminho para arquivo de log (opcional)
    """
    UtilLog.configurar_logging(nivel, arquivo_log)

def versao():
    """Retorna versão do módulo"""
    return __version__
