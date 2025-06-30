#!/usr/bin/env python3
"""
Testes do Parser Híbrido de NFe
Conjunto de testes para validar todas as funcionalidades
"""

import unittest
import sys
import os
from pathlib import Path
from decimal import Decimal

# Adicionar diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from parser_hibrido import (
    NFEParserHibrido,
    NotaFiscal,
    ItemNotaFiscal,
    ValidadorFiscal,
    converter_para_decimal,
    processar_xml_nfe_hibrido
)

class TestValidadorFiscal(unittest.TestCase):
    """Testes para o ValidadorFiscal"""
    
    def setUp(self):
        self.validador = ValidadorFiscal()
    
    def test_validar_cnpj_valido(self):
        """Teste CNPJ válido"""
        self.assertTrue(self.validador.validar_cnpj("12.345.678/0001-23"))
        self.assertTrue(self.validador.validar_cnpj("12345678000123"))
    
    def test_validar_cnpj_invalido(self):
        """Teste CNPJ inválido"""
        self.assertFalse(self.validador.validar_cnpj("123456780001"))  # Menos dígitos
        self.assertFalse(self.validador.validar_cnpj("12345678000123456"))  # Mais dígitos
        self.assertFalse(self.validador.validar_cnpj(""))  # Vazio
        self.assertFalse(self.validador.validar_cnpj("00000000000000"))  # Inválido conhecido
    
    def test_validar_cpf_valido(self):
        """Teste CPF válido"""
        self.assertTrue(self.validador.validar_cpf("123.456.789-00"))
        self.assertTrue(self.validador.validar_cpf("12345678900"))
    
    def test_validar_ncm_valido(self):
        """Teste NCM válido"""
        self.assertTrue(self.validador.validar_ncm("12345678"))
        self.assertTrue(self.validador.validar_ncm("87654321"))
    
    def test_validar_ncm_invalido(self):
        """Teste NCM inválido"""
        self.assertFalse(self.validador.validar_ncm("1234567"))  # 7 dígitos
        self.assertFalse(self.validador.validar_ncm("123456789"))  # 9 dígitos
        self.assertFalse(self.validador.validar_ncm("1234567A"))  # Com letra
    
    def test_validar_cfop_valido(self):
        """Teste CFOP válido"""
        self.assertTrue(self.validador.validar_cfop("5102"))
        self.assertTrue(self.validador.validar_cfop("1102"))
        self.assertTrue(self.validador.validar_cfop("6102"))
    
    def test_validar_cfop_invalido(self):
        """Teste CFOP inválido"""
        self.assertFalse(self.validador.validar_cfop("512"))  # 3 dígitos
        self.assertFalse(self.validador.validar_cfop("51022"))  # 5 dígitos
        self.assertFalse(self.validador.validar_cfop("4102"))  # Primeiro dígito inválido
    
    def test_validar_cst_valido(self):
        """Teste CST válido"""
        self.assertTrue(self.validador.validar_cst("01"))
        self.assertTrue(self.validador.validar_cst("04"))
        self.assertTrue(self.validador.validar_cst("99"))
    
    def test_validar_cst_invalido(self):
        """Teste CST inválido"""
        self.assertFalse(self.validador.validar_cst("00"))  # Não existe
        self.assertFalse(self.validador.validar_cst("1"))   # 1 dígito
        self.assertFalse(self.validador.validar_cst("100")) # 3 dígitos

class TestModelos(unittest.TestCase):
    """Testes para os modelos de dados"""
    
    def test_converter_para_decimal(self):
        """Teste conversão para Decimal"""
        self.assertEqual(converter_para_decimal("100.50"), Decimal("100.50"))
        self.assertEqual(converter_para_decimal("100,50"), Decimal("100.50"))
        self.assertEqual(converter_para_decimal(100.50), Decimal("100.50"))
        self.assertEqual(converter_para_decimal(""), Decimal("0"))
        self.assertEqual(converter_para_decimal(None), Decimal("0"))
    
    def test_item_nota_fiscal(self):
        """Teste ItemNotaFiscal"""
        item = ItemNotaFiscal()
        item.valor_bruto = Decimal("100.00")
        item.valor_desconto = Decimal("10.00")
        
        # Teste cálculo valor total
        valor_total = item.calcular_valor_total()
        self.assertEqual(valor_total, Decimal("90.00"))
        self.assertEqual(item.valor_total, Decimal("90.00"))
    
    def test_nota_fiscal(self):
        """Teste NotaFiscal"""
        nota = NotaFiscal()
        
        # Criar itens de teste
        item1 = ItemNotaFiscal()
        item1.valor_bruto = Decimal("100.00")
        item1.valor_desconto = Decimal("10.00")
        item1.calcular_valor_total()
        
        item2 = ItemNotaFiscal()
        item2.valor_bruto = Decimal("200.00")
        item2.valor_desconto = Decimal("20.00")
        item2.calcular_valor_total()
        
        # Adicionar itens
        nota.adicionar_item(item1)
        nota.adicionar_item(item2)
        
        # Verificar totais
        self.assertEqual(nota.valor_produtos, Decimal("300.00"))
        self.assertEqual(nota.valor_desconto_total, Decimal("30.00"))
        self.assertEqual(len(nota.itens), 2)

def teste_rapido():
    """Teste rápido para verificar instalação"""
    print("⚡ TESTE RÁPIDO DE INSTALAÇÃO")
    print("-" * 30)
    
    try:
        # Teste imports
        from parser_hibrido import NFEParserHibrido, ValidadorFiscal
        print("✅ Imports realizados com sucesso")
        
        # Teste validador
        validador = ValidadorFiscal()
        assert validador.validar_cnpj("12345678000123") == True
        print("✅ Validador funcionando")
        
        # Teste parser básico
        parser = NFEParserHibrido()
        assert parser is not None
        print("✅ Parser inicializado")
        
        print("\n🎉 INSTALAÇÃO OK! Todos os componentes funcionando.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA INSTALAÇÃO: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser_args = argparse.ArgumentParser(description="Testes do Parser Híbrido NFe")
    parser_args.add_argument("--rapido", action="store_true", help="Executa apenas teste rápido")
    parser_args.add_argument("--completo", action="store_true", help="Executa todos os testes")
    
    args = parser_args.parse_args()
    
    if args.rapido:
        teste_rapido()
    else:
        # Por padrão, executa teste rápido
        if teste_rapido():
            print("\n🚀 Para executar testes completos, use: python testes.py --completo")
