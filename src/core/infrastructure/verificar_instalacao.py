#!/usr/bin/env python3
"""
Script de Verificação Final - Parser Híbrido NFe
Verifica se a instalação está completa e funcionando
"""

import os
import sys
from pathlib import Path

def verificar_instalacao():
    """Verifica se a instalação está completa"""
    print("🔍 VERIFICAÇÃO FINAL DO PARSER HÍBRIDO")
    print("=" * 50)
    
    # Verificar estrutura de arquivos
    arquivos_necessarios = [
        "__init__.py",
        "parser_hibrido.py", 
        "models.py",
        "validators.py",
        "utils.py",
        "testes.py",
        "exemplo_uso.py",
        "migracao_sistema.py",
        "requirements.txt",
        "README.md"
    ]
    
    print("📁 Verificando arquivos...")
    diretorio_atual = Path(__file__).parent
    
    for arquivo in arquivos_necessarios:
        caminho = diretorio_atual / arquivo
        if caminho.exists():
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - FALTANDO")
            return False
    
    # Testar imports
    print("\n📦 Testando imports...")
    try:
        sys.path.insert(0, str(diretorio_atual))
        
        from validators import ValidadorFiscal
        print("   ✅ ValidadorFiscal")
        
        from models import NotaFiscal, ItemNotaFiscal
        print("   ✅ NotaFiscal, ItemNotaFiscal")
        
        from parser_hibrido import NFEParserHibrido
        print("   ✅ NFEParserHibrido")
        
        from utils import UtilXML, UtilData
        print("   ✅ Utilitários")
        
    except ImportError as e:
        print(f"   ❌ Erro de import: {e}")
        return False
    
    # Teste funcional básico
    print("\n🧪 Testando funcionalidades...")
    try:
        # Teste validador
        validador = ValidadorFiscal()
        assert validador.validar_cnpj("12345678000123") == True
        print("   ✅ Validação CNPJ")
        
        # Teste parser
        parser = NFEParserHibrido()
        assert parser is not None
        print("   ✅ Parser inicializado")
        
        # Teste modelos
        nota = NotaFiscal()
        item = ItemNotaFiscal()
        assert nota is not None and item is not None
        print("   ✅ Modelos funcionando")
        
    except Exception as e:
        print(f"   ❌ Erro funcional: {e}")
        return False
    
    print("\n✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Executar testes: python testes.py --rapido")
    print("   2. Ver exemplos: python exemplo_uso.py")
    print("   3. Migrar sistema: python migracao_sistema.py --migrar")
    
    return True

if __name__ == "__main__":
    verificar_instalacao()
