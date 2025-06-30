#!/usr/bin/env python3
"""
Validadores Fiscais Robustos
Implementa validações específicas para documentos fiscais brasileiros
"""

import re
import logging
from typing import Optional, List

# Configurar logging
logger = logging.getLogger(__name__)

class ValidadorFiscal:
    """Classe com validadores fiscais robustos baseados na legislação brasileira"""
    
    def __init__(self):
        self.logs_validacao = []
        
        # CSTs válidos para PIS/COFINS conforme legislação
        self.csts_validos = [
            '01', '02', '03', '04', '05', '06', '07', '08', '09', 
            '49', '50', '51', '52', '53', '54', '55', '56', 
            '60', '61', '62', '63', '64', '65', '66', '67', 
            '70', '71', '72', '73', '74', '75', '98', '99'
        ]
        
        # CSTs que indicam produtos monofásicos
        self.csts_monofasicos = ['04', '05', '06']
    
    def validar_cnpj(self, cnpj: str) -> bool:
        """
        Validação robusta de CNPJ
        Args:
            cnpj: String do CNPJ a ser validado
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cnpj:
            self._log_validacao("CNPJ vazio ou None", "WARNING")
            return False
        
        # Remove formatação
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj_numeros) != 14:
            self._log_validacao(f"CNPJ com {len(cnpj_numeros)} dígitos (esperado: 14): {cnpj}", "ERROR")
            return False
        
        # Verifica se são todos números
        if not cnpj_numeros.isdigit():
            self._log_validacao(f"CNPJ contém caracteres não numéricos: {cnpj}", "ERROR")
            return False
        
        # Validação adicional: CNPJs inválidos conhecidos
        cnpjs_invalidos = ['00000000000000', '11111111111111', '22222222222222']
        if cnpj_numeros in cnpjs_invalidos:
            self._log_validacao(f"CNPJ inválido conhecido: {cnpj}", "ERROR")
            return False
        
        return True
    
    def validar_cpf(self, cpf: str) -> bool:
        """
        Validação robusta de CPF
        Args:
            cpf: String do CPF a ser validado
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cpf:
            self._log_validacao("CPF vazio ou None", "WARNING")
            return False
        
        # Remove formatação
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            self._log_validacao(f"CPF com {len(cpf_numeros)} dígitos (esperado: 11): {cpf}", "ERROR")
            return False
        
        # Verifica se são todos números
        if not cpf_numeros.isdigit():
            self._log_validacao(f"CPF contém caracteres não numéricos: {cpf}", "ERROR")
            return False
        
        return True
    
    def validar_ncm(self, ncm: str) -> bool:
        """
        Validação de NCM (Nomenclatura Comum do Mercosul)
        Args:
            ncm: String do NCM a ser validado
        Returns:
            bool: True se válido, False caso contrário
        """
        if not ncm:
            self._log_validacao("NCM vazio ou None", "WARNING")
            return False
        
        # Remove espaços e formatação
        ncm_limpo = re.sub(r'\D', '', ncm.strip())
        
        # NCM deve ter exatamente 8 dígitos
        if len(ncm_limpo) != 8:
            self._log_validacao(f"NCM com {len(ncm_limpo)} dígitos (esperado: 8): {ncm}", "ERROR")
            return False
        
        # Verifica se são todos números
        if not ncm_limpo.isdigit():
            self._log_validacao(f"NCM contém caracteres não numéricos: {ncm}", "ERROR")
            return False
        
        return True
    
    def validar_cfop(self, cfop: str) -> bool:
        """
        Validação de CFOP (Código Fiscal de Operações e Prestações)
        Args:
            cfop: String do CFOP a ser validado
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cfop:
            self._log_validacao("CFOP vazio ou None", "WARNING")
            return False
        
        # Remove espaços e formatação
        cfop_limpo = re.sub(r'\D', '', cfop.strip())
        
        # CFOP deve ter exatamente 4 dígitos
        if len(cfop_limpo) != 4:
            self._log_validacao(f"CFOP com {len(cfop_limpo)} dígitos (esperado: 4): {cfop}", "ERROR")
            return False
        
        # Verifica se são todos números
        if not cfop_limpo.isdigit():
            self._log_validacao(f"CFOP contém caracteres não numéricos: {cfop}", "ERROR")
            return False
        
        # Validação adicional: primeiro dígito deve ser 1, 2, 3, 5, 6 ou 7
        primeiro_digito = cfop_limpo[0]
        if primeiro_digito not in ['1', '2', '3', '5', '6', '7']:
            self._log_validacao(f"CFOP com primeiro dígito inválido: {cfop}", "ERROR")
            return False
        
        return True
    
    def validar_cst(self, cst: str, tipo: str = "PIS/COFINS") -> bool:
        """
        Validação de CST (Código de Situação Tributária)
        Args:
            cst: String do CST a ser validado
            tipo: Tipo do CST (PIS/COFINS, ICMS, IPI)
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cst:
            self._log_validacao(f"CST {tipo} vazio ou None", "WARNING")
            return False
        
        # Remove espaços
        cst_limpo = cst.strip()
        
        # CST deve ter 2 dígitos para PIS/COFINS
        if tipo == "PIS/COFINS":
            if len(cst_limpo) != 2:
                self._log_validacao(f"CST {tipo} com {len(cst_limpo)} dígitos (esperado: 2): {cst}", "ERROR")
                return False
            
            if cst_limpo not in self.csts_validos:
                self._log_validacao(f"CST {tipo} inválido: {cst}", "ERROR")
                return False
        
        return True
    
    def validar_chave_nfe(self, chave: str) -> bool:
        """
        Validação de chave de acesso da NFe
        Args:
            chave: String da chave de acesso
        Returns:
            bool: True se válida, False caso contrário
        """
        if not chave:
            self._log_validacao("Chave de acesso vazia ou None", "ERROR")
            return False
        
        # Remove formatação e prefixos
        chave_limpa = re.sub(r'\D', '', chave)
        if chave_limpa.startswith('NFe'):
            chave_limpa = chave_limpa[3:]
        
        # Chave deve ter exatamente 44 dígitos
        if len(chave_limpa) != 44:
            self._log_validacao(f"Chave com {len(chave_limpa)} dígitos (esperado: 44): {chave}", "ERROR")
            return False
        
        # Verifica se são todos números
        if not chave_limpa.isdigit():
            self._log_validacao(f"Chave contém caracteres não numéricos: {chave}", "ERROR")
            return False
        
        return True
    
    def eh_produto_monofasico_por_cst(self, pis_cst: str, cofins_cst: str) -> bool:
        """
        Verifica se produto é monofásico baseado nos CSTs de PIS/COFINS
        Args:
            pis_cst: CST do PIS
            cofins_cst: CST do COFINS
        Returns:
            bool: True se monofásico, False caso contrário
        """
        # CSTs que indicam tributação monofásica
        return (pis_cst in self.csts_monofasicos or 
                cofins_cst in self.csts_monofasicos)
    
    def validar_valor_monetario(self, valor: str) -> bool:
        """
        Validação de valores monetários
        Args:
            valor: String do valor a ser validado
        Returns:
            bool: True se válido, False caso contrário
        """
        if not valor:
            return True  # Valor vazio é aceitável
        
        # Remove espaços
        valor_limpo = valor.strip()
        
        # Substitui vírgula por ponto
        valor_limpo = valor_limpo.replace(',', '.')
        
        # Verifica formato numérico
        if not re.match(r'^\d+\.?\d*$', valor_limpo):
            self._log_validacao(f"Valor monetário inválido: {valor}", "ERROR")
            return False
        
        return True
    
    def _log_validacao(self, mensagem: str, nivel: str = "INFO"):
        """
        Registra log de validação
        Args:
            mensagem: Mensagem do log
            nivel: Nível do log (INFO, WARNING, ERROR)
        """
        self.logs_validacao.append(f"[{nivel}] {mensagem}")
        
        if nivel == "ERROR":
            logger.error(mensagem)
        elif nivel == "WARNING":
            logger.warning(mensagem)
        else:
            logger.info(mensagem)
    
    def obter_logs_validacao(self) -> List[str]:
        """
        Retorna lista de logs de validação
        Returns:
            List[str]: Lista com todos os logs
        """
        return self.logs_validacao.copy()
    
    def limpar_logs(self):
        """Limpa logs de validação"""
        self.logs_validacao.clear()
    
    def validar_ie(self, ie: str, uf: Optional[str] = None) -> bool:
        """
        Validação básica de Inscrição Estadual
        Args:
            ie: String da IE
            uf: UF para validação específica (opcional)
        Returns:
            bool: True se válida, False caso contrário
        """
        if not ie:
            return True  # IE pode ser vazia
        
        ie_limpa = re.sub(r'\D', '', ie.strip())
        
        # IE deve ter entre 8 e 15 dígitos
        if len(ie_limpa) < 8 or len(ie_limpa) > 15:
            self._log_validacao(f"IE com {len(ie_limpa)} dígitos (esperado: 8-15): {ie}", "WARNING")
            return False
        
        return True
