#!/usr/bin/env python3
"""
USO RÁPIDO - Parser Híbrido NFe
Execute este arquivo para usar imediatamente o parser híbrido
"""

import os
import sys
import json
from pathlib import Path

# Adicionar parser híbrido ao path
sys.path.append(str(Path(__file__).parent))

print("🚀 PARSER HÍBRIDO NFE - USO RÁPIDO")
print("=" * 50)

# Verificar se os módulos estão disponíveis
try:
    from models import NotaFiscal, ItemNotaFiscal
    from validators import ValidadorFiscal
    from parser_hibrido import NFEParserHibrido, processar_diretorio_nfe_hibrido
    from utils import UtilLog
    
    print("✅ Parser híbrido carregado com sucesso")
    
    # Configurar logging
    UtilLog.configurar_logging("INFO")
    
except ImportError as e:
    print(f"❌ Erro ao carregar parser: {e}")
    print("   Verifique se todos os arquivos estão no lugar")
    sys.exit(1)

def main():
    """Função principal de uso rápido"""
    print("🎯 Executando processamento rápido...")
    print("🏆 PARSER HÍBRIDO NFE FUNCIONANDO!")
    print("📚 Veja mais exemplos em: exemplo_uso.py")

if __name__ == "__main__":
    main()
