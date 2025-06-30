#!/usr/bin/env python3
"""
Modelos de Dados Aprimorados para NFe
Classes orientadas a objeto com validação e precisão fiscal
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class ItemNotaFiscal:
    """Classe para representar um item de nota fiscal com validação robusta"""
    
    def __init__(self):
        # Dados básicos do item
        self.numero: int = 0
        self.codigo: str = ""
        self.ean: str = ""
        self.descricao: str = ""
        
        # Classificação fiscal
        self.ncm: str = ""
        self.cest: str = ""
        self.cfop: str = ""
        
        # Dados comerciais
        self.unidade: str = ""
        self.quantidade: Decimal = Decimal('0')
        self.valor_unitario: Decimal = Decimal('0')
        
        # Valores do produto
        self.valor_bruto: Decimal = Decimal('0')  # vProd
        self.valor_desconto: Decimal = Decimal('0')  # vDesc
        self.valor_total: Decimal = Decimal('0')  # valor_bruto - valor_desconto
        
        # Tributos PIS
        self.pis_cst: str = ""
        self.pis_base_calculo: Decimal = Decimal('0')
        self.pis_aliquota: Decimal = Decimal('0')
        self.pis_valor: Decimal = Decimal('0')
        self.pis_subgrupo: str = ""  # PISAliq, PISNT, etc.
        
        # Tributos COFINS
        self.cofins_cst: str = ""
        self.cofins_base_calculo: Decimal = Decimal('0')
        self.cofins_aliquota: Decimal = Decimal('0')
        self.cofins_valor: Decimal = Decimal('0')
        self.cofins_subgrupo: str = ""  # COFINSAliq, COFINSNT, etc.
        
        # Classificação tributária
        self.tipo_tributario: str = ""  # "Monofasico" ou "NaoMonofasico"
        self.eh_monofasico_por_ncm: bool = False
        self.eh_monofasico_por_cst: bool = False
        
        # Validação
        self.valido: bool = True
        self.erros_validacao: List[str] = []
    
    def calcular_valor_total(self):
        """Calcula o valor total do item (bruto - desconto)"""
        self.valor_total = self.valor_bruto - self.valor_desconto
        return self.valor_total
    
    def adicionar_erro_validacao(self, erro: str):
        """Adiciona erro de validação ao item"""
        self.erros_validacao.append(erro)
        self.valido = False
    
    def obter_valor_base_tributacao(self) -> Decimal:
        """
        Retorna o valor base para cálculo de tributação
        Normalmente é o valor total (bruto - desconto)
        """
        return self.valor_total
    
    def eh_isento_pis_cofins(self) -> bool:
        """Verifica se o item é isento de PIS/COFINS"""
        csts_isentos = ['04', '05', '06', '07', '08', '09']
        return (self.pis_cst in csts_isentos or 
                self.cofins_cst in csts_isentos)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte item para dicionário com valores serializáveis"""
        return {
            "numero": self.numero,
            "codigo": self.codigo,
            "ean": self.ean,
            "descricao": self.descricao,
            "ncm": self.ncm,
            "cest": self.cest,
            "cfop": self.cfop,
            "unidade": self.unidade,
            "quantidade": float(self.quantidade),
            "valor_unitario": float(self.valor_unitario),
            "valor_bruto": float(self.valor_bruto),
            "valor_desconto": float(self.valor_desconto),
            "valor_total": float(self.valor_total),
            "pis": {
                "cst": self.pis_cst,
                "base_calculo": float(self.pis_base_calculo),
                "aliquota": float(self.pis_aliquota),
                "valor": float(self.pis_valor),
                "subgrupo": self.pis_subgrupo
            },
            "cofins": {
                "cst": self.cofins_cst,
                "base_calculo": float(self.cofins_base_calculo),
                "aliquota": float(self.cofins_aliquota),
                "valor": float(self.cofins_valor),
                "subgrupo": self.cofins_subgrupo
            },
            "tributacao": {
                "tipo": self.tipo_tributario,
                "monofasico_por_ncm": self.eh_monofasico_por_ncm,
                "monofasico_por_cst": self.eh_monofasico_por_cst,
                "isento_pis_cofins": self.eh_isento_pis_cofins()
            },
            "validacao": {
                "valido": self.valido,
                "erros": self.erros_validacao
            }
        }
    
    def __str__(self) -> str:
        return (f"Item {self.numero}: {self.descricao[:50]} | "
                f"NCM: {self.ncm} | CFOP: {self.cfop} | "
                f"PIS CST: {self.pis_cst} | COFINS CST: {self.cofins_cst} | "
                f"Valor: R$ {self.valor_total:.2f} | "
                f"Tipo: {self.tipo_tributario}")

class NotaFiscal:
    """Classe para representar uma nota fiscal completa com validação robusta"""
    
    def __init__(self):
        # Identificação da nota
        self.chave_acesso: str = ""
        self.numero: str = ""
        self.serie: str = ""
        self.modelo: str = ""
        self.data_emissao: Optional[datetime] = None
        self.natureza_operacao: str = ""
        self.codigo_uf: str = ""
        
        # Dados do emitente
        self.emitente_cnpj: str = ""
        self.emitente_nome: str = ""
        self.emitente_ie: str = ""
        self.emitente_endereco: Dict[str, str] = {}
        
        # Dados do destinatário
        self.destinatario_cnpj_cpf: str = ""
        self.destinatario_nome: str = ""
        self.destinatario_ie: str = ""
        self.destinatario_endereco: Dict[str, str] = {}
        
        # Valores totais da nota
        self.valor_produtos: Decimal = Decimal('0')  # vProd
        self.valor_total_nf: Decimal = Decimal('0')  # vNF
        self.valor_desconto_total: Decimal = Decimal('0')  # vDesc
        self.valor_pis_total: Decimal = Decimal('0')
        self.valor_cofins_total: Decimal = Decimal('0')
        
        # Itens da nota
        self.itens: List[ItemNotaFiscal] = []
        
        # Status e validação
        self.status: str = "ATIVO"  # ATIVO, CANCELADO, INUTILIZADO
        self.valida: bool = True
        self.erros_validacao: List[str] = []
        self.logs_processamento: List[str] = []
        
        # Informações adicionais
        self.informacoes_adicionais: str = ""
        
        # Metadados de processamento
        self.data_processamento: Optional[datetime] = None
        self.arquivo_origem: str = ""
    
    def adicionar_item(self, item: ItemNotaFiscal):
        """Adiciona item à nota fiscal"""
        self.itens.append(item)
        self.recalcular_totais()
    
    def recalcular_totais(self):
        """Recalcula totais da nota baseado nos itens"""
        self.valor_produtos = sum(item.valor_bruto for item in self.itens)
        self.valor_desconto_total = sum(item.valor_desconto for item in self.itens)
        self.valor_pis_total = sum(item.pis_valor for item in self.itens)
        self.valor_cofins_total = sum(item.cofins_valor for item in self.itens)
        
        # Valor total calculado (pode diferir do XML em casos específicos)
        valor_calculado = self.valor_produtos - self.valor_desconto_total
        
        return valor_calculado
    
    def adicionar_erro_validacao(self, erro: str):
        """Adiciona erro de validação à nota"""
        self.erros_validacao.append(erro)
        self.valida = False
    
    def adicionar_log_processamento(self, log: str):
        """Adiciona log de processamento"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs_processamento.append(f"[{timestamp}] {log}")
    
    def obter_itens_monofasicos(self) -> List[ItemNotaFiscal]:
        """Retorna lista de itens classificados como monofásicos"""
        return [item for item in self.itens if item.tipo_tributario == "Monofasico"]
    
    def obter_itens_nao_monofasicos(self) -> List[ItemNotaFiscal]:
        """Retorna lista de itens não-monofásicos"""
        return [item for item in self.itens if item.tipo_tributario == "NaoMonofasico"]
    
    def obter_valor_total_monofasicos(self) -> Decimal:
        """Retorna valor total dos produtos monofásicos"""
        return sum(item.valor_total for item in self.obter_itens_monofasicos())
    
    def obter_valor_total_nao_monofasicos(self) -> Decimal:
        """Retorna valor total dos produtos não-monofásicos"""
        return sum(item.valor_total for item in self.obter_itens_nao_monofasicos())
    
    def obter_proporcao_monofasicos(self) -> Decimal:
        """Retorna proporção de produtos monofásicos (0-100)"""
        total_geral = self.obter_valor_total_monofasicos() + self.obter_valor_total_nao_monofasicos()
        if total_geral == 0:
            return Decimal('0')
        
        proporcao = (self.obter_valor_total_monofasicos() / total_geral) * 100
        return proporcao.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def eh_nota_cancelada(self) -> bool:
        """Verifica se a nota está cancelada"""
        return self.status == "CANCELADO"
    
    def marcar_como_cancelada(self, motivo: str = ""):
        """Marca nota como cancelada"""
        self.status = "CANCELADO"
        if motivo:
            self.adicionar_log_processamento(f"Nota cancelada: {motivo}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas da nota fiscal"""
        return {
            "total_itens": len(self.itens),
            "itens_monofasicos": len(self.obter_itens_monofasicos()),
            "itens_nao_monofasicos": len(self.obter_itens_nao_monofasicos()),
            "valor_total_monofasicos": float(self.obter_valor_total_monofasicos()),
            "valor_total_nao_monofasicos": float(self.obter_valor_total_nao_monofasicos()),
            "proporcao_monofasicos": float(self.obter_proporcao_monofasicos()),
            "valor_pis_total": float(self.valor_pis_total),
            "valor_cofins_total": float(self.valor_cofins_total),
            "status": self.status,
            "valida": self.valida
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte nota fiscal para dicionário com valores serializáveis"""
        return {
            "identificacao": {
                "chave_acesso": self.chave_acesso,
                "numero": self.numero,
                "serie": self.serie,
                "modelo": self.modelo,
                "data_emissao": self.data_emissao.isoformat() if self.data_emissao else None,
                "natureza_operacao": self.natureza_operacao,
                "codigo_uf": self.codigo_uf
            },
            "emitente": {
                "cnpj": self.emitente_cnpj,
                "nome": self.emitente_nome,
                "ie": self.emitente_ie,
                "endereco": self.emitente_endereco
            },
            "destinatario": {
                "cnpj_cpf": self.destinatario_cnpj_cpf,
                "nome": self.destinatario_nome,
                "ie": self.destinatario_ie,
                "endereco": self.destinatario_endereco
            },
            "totais": {
                "valor_produtos": float(self.valor_produtos),
                "valor_total_nf": float(self.valor_total_nf),
                "valor_desconto_total": float(self.valor_desconto_total),
                "valor_pis_total": float(self.valor_pis_total),
                "valor_cofins_total": float(self.valor_cofins_total)
            },
            "itens": [item.to_dict() for item in self.itens],
            "status": self.status,
            "validacao": {
                "valida": self.valida,
                "erros": self.erros_validacao
            },
            "metadados": {
                "data_processamento": self.data_processamento.isoformat() if self.data_processamento else None,
                "arquivo_origem": self.arquivo_origem,
                "logs_processamento": self.logs_processamento
            },
            "estatisticas": self.obter_estatisticas(),
            "informacoes_adicionais": self.informacoes_adicionais
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Converte nota fiscal para JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __str__(self) -> str:
        return (f"NFe {self.numero}-{self.serie} | "
                f"Chave: {self.chave_acesso[:10]}... | "
                f"Emitente: {self.emitente_nome} | "
                f"Total: R$ {self.valor_total_nf:.2f} | "
                f"Itens: {len(self.itens)} | "
                f"Status: {self.status}")

class EventoCancelamento:
    """Classe para representar eventos de cancelamento de NFe"""
    
    def __init__(self):
        self.chave_nfe: str = ""
        self.tipo_evento: str = "110111"  # Cancelamento
        self.data_evento: Optional[datetime] = None
        self.justificativa: str = ""
        self.numero_protocolo: str = ""
        self.numero_sequencial: int = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário"""
        return {
            "chave_nfe": self.chave_nfe,
            "tipo_evento": self.tipo_evento,
            "data_evento": self.data_evento.isoformat() if self.data_evento else None,
            "justificativa": self.justificativa,
            "numero_protocolo": self.numero_protocolo,
            "numero_sequencial": self.numero_sequencial
        }

def converter_para_decimal(valor: Any) -> Decimal:
    """
    Converte valor para Decimal com tratamento seguro
    Args:
        valor: Valor a ser convertido
    Returns:
        Decimal: Valor convertido ou Decimal('0') se conversão falhar
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
        return Decimal('0')
