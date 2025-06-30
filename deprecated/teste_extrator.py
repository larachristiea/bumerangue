#!/usr/bin/env python3
"""
TESTE RÁPIDO DO EXTRATOR DE PGDAS
Verifica se o extrator está funcionando corretamente
"""

import os
import sys
import argparse
import importlib

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import pdfplumber
        print("✅ pdfplumber: OK")
    except ImportError:
        print("❌ pdfplumber: NÃO INSTALADO")
        print("   Execute: pip install pdfplumber")
        return False
    
    try:
        import json
        import re
        import logging
        from datetime import datetime
        print("✅ Bibliotecas padrão: OK")
    except ImportError:
        print("❌ Bibliotecas padrão: ERRO")
        return False
    
    return True

def verificar_estrutura_diretorios(base_dir):
    """Verifica se a estrutura de diretórios está correta"""
    print("\n📁 Verificando estrutura de diretórios...")
    
    if not os.path.exists(base_dir):
        print(f"❌ Diretório base não encontrado: {base_dir}")
        return False
    else:
        print(f"✅ Diretório base: OK")
    
    pdfs_encontrados = 0
    
    for root, _, files in os.walk(base_dir):
        pdfs = [f for f in files if f.lower().endswith('.pdf')]
        if pdfs:
            print(f"✅ {root}: {len(pdfs)} PDFs encontrados")
            pdfs_encontrados += len(pdfs)
    
    print(f"📊 Total de PDFs para processar: {pdfs_encontrados}")
    
    return pdfs_encontrados > 0

def testar_extrator_simples(module_name='extrator_pgdas_pdf', class_name='ExtratorPGDAS'):
    """Testa o extrator com um PDF de exemplo usando importação dinâmica"""
    print("\n🧪 Testando extrator...")
    try:
        module = importlib.import_module(module_name)
        extrator_cls = getattr(module, class_name)
        extrator = extrator_cls()
        print("✅ Extrator carregado com sucesso")
        
        # Verificar template
        template = extrator.template_json
        if template and "dados_estruturados" in template:
            print("✅ Template JSON: OK")
        else:
            print("❌ Template JSON: ERRO")
            return False
        
        # Testar conversão de valores
        teste_valor = extrator.converter_valor_monetario("1.234,56")
        if teste_valor == 1234.56:
            print("✅ Conversão monetária: OK")
        else:
            print("❌ Conversão monetária: ERRO")
            return False
        
        print("✅ Todos os testes básicos passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar extrator: {str(e)}")
        return False

def main():
    """Função principal do teste"""
    print("🔧 TESTE RÁPIDO - EXTRATOR DE PGDAS")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description="Teste rápido do extrator de PGDAS.")
    parser.add_argument('--input', required=True, help='Diretório base de entrada dos PDFs')
    parser.add_argument('--extrator-module', default='extrator_pgdas_pdf', help='Módulo do extrator (padrão: extrator_pgdas_pdf)')
    parser.add_argument('--extrator-class', default='ExtratorPGDAS', help='Classe do extrator (padrão: ExtratorPGDAS)')
    args = parser.parse_args()
    
    # Passo 1: Verificar dependências
    if not verificar_dependencias():
        print("\n❌ FALHA: Dependências não atendidas")
        print("Execute: pip install -r requirements_extrator.txt")
        return
    
    # Passo 2: Verificar estrutura
    if not verificar_estrutura_diretorios(args.input):
        print("\n❌ FALHA: Nenhum PDF encontrado para processar")
        print("Verifique se os PDFs estão nas pastas corretas")
        return
    
    # Passo 3: Testar extrator
    if not testar_extrator_simples(args.extrator_module, args.extrator_class):
        print("\n❌ FALHA: Erro no extrator")
        return
    
    print("\n" + "=" * 50)
    print("🎉 SUCESSO! O extrator está pronto para usar!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python3 extrator_pgdas_pdf.py --input <diretorio_de_entrada> --output <diretorio_de_saida>")
    print("2. Aguarde o processamento dos PDFs")
    print("3. Verifique os JSONs gerados na pasta de saída indicada")
    print("\n✨ Boa sorte com a extração automática!")

if __name__ == "__main__":
    main()
