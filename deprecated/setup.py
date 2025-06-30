#!/usr/bin/env python3
"""
Setup e Instalação - Parser Híbrido NFe
Automatiza instalação e configuração inicial
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def verificar_python():
    """Verifica versão do Python"""
    print("🐍 Verificando Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Necessário Python 3.6+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def instalar_dependencias():
    """Instala dependências necessárias"""
    print("\n📦 Instalando dependências...")
    
    try:
        # Verificar se requirements.txt existe
        if not os.path.exists('requirements.txt'):
            print("❌ Arquivo requirements.txt não encontrado")
            return False
        
        # Instalar dependências
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso")
            return True
        else:
            print(f"❌ Erro na instalação: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def verificar_dependencias():
    """Verifica se dependências estão instaladas"""
    print("\n🔍 Verificando dependências...")
    
    dependencias = ['lxml']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} não encontrado")
            return False
    
    return True

def testar_parser():
    """Testa funcionamento básico do parser"""
    print("\n🧪 Testando parser híbrido...")
    
    try:
        # Import básico
        from parser_hibrido import NFEParserHibrido, configurar_logging
        print("✅ Import do parser: OK")
        
        # Configurar logging
        configurar_logging("INFO")
        print("✅ Configuração de logging: OK")
        
        # Teste básico com validador
        from parser_hibrido import ValidadorFiscal
        validador = ValidadorFiscal()
        
        # Teste de validação
        if validador.validar_cnpj("12345678000123"):
            print("✅ Validador CNPJ: OK")
        
        if validador.validar_ncm("12345678"):
            print("✅ Validador NCM: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def criar_estrutura_diretorios():
    """Cria estrutura de diretórios necessária"""
    print("\n📁 Criando estrutura de diretórios...")
    
    diretorios = [
        'data',
        'data/xmls',
        'data/tabelas',
        'data/pgdas',
        'data/resultados',
        'logs'
    ]
    
    for diretorio in diretorios:
        try:
            os.makedirs(diretorio, exist_ok=True)
            print(f"✅ {diretorio}/")
        except Exception as e:
            print(f"❌ Erro ao criar {diretorio}: {e}")
            return False
    
    return True

def criar_arquivo_exemplo():
    """Cria arquivo de exemplo de configuração"""
    print("\n📝 Criando arquivos de exemplo...")
    
    # Configuração exemplo
    config_exemplo = {
        "logging": {
            "nivel": "INFO",
            "arquivo": "logs/parser_nfe.log"
        },
        "paths": {
            "xmls": "data/xmls",
            "tabelas": "data/tabelas",
            "pgdas": "data/pgdas",
            "resultados": "data/resultados"
        },
        "parser": {
            "incluir_cancelamentos": True,
            "validacao_rigorosa": True,
            "salvar_logs_validacao": True
        }
    }
    
    try:
        with open('config_exemplo.json', 'w', encoding='utf-8') as f:
            json.dump(config_exemplo, f, indent=2, ensure_ascii=False)
        print("✅ config_exemplo.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivos: {e}")
        return False

def criar_script_uso_rapido():
    """Cria script de uso rápido"""
    print("\n⚡ Criando script de uso rápido...")
    
    script_content = '''#!/usr/bin/env python3
"""
Uso Rápido - Parser Híbrido NFe
Script para uso imediato do parser
"""

import json
from parser_hibrido import processar_diretorio_nfe_hibrido, configurar_logging

def main():
    """Função principal de uso rápido"""
    print("🚀 PARSER HÍBRIDO NFE - USO RÁPIDO")
    print("=" * 40)
    
    # Configurar logging
    configurar_logging("INFO", "logs/parser_nfe.log")
    
    # Carregar configuração
    try:
        with open('config_exemplo.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Configuração carregada")
    except:
        print("⚠️  Usando configuração padrão")
        config = {
            "paths": {
                "xmls": "data/xmls",
                "tabelas": "data/tabelas"
            }
        }
    
    # Carregar tabela NCM se disponível
    tabela_ncm = {}
    try:
        with open(f"{config['paths']['tabelas']}/Espelho de ncms monofásicas.json", 'r', encoding='utf-8') as f:
            tabela_ncm = json.load(f)
        print(f"✅ Tabela NCM carregada: {len(tabela_ncm)} NCMs")
    except:
        print("⚠️  Tabela NCM não encontrada")
    
    # Diretório de XMLs
    diretorio_xmls = config['paths']['xmls']
    
    if not os.path.exists(diretorio_xmls):
        print(f"❌ Diretório de XMLs não encontrado: {diretorio_xmls}")
        print("   Coloque seus XMLs em data/xmls/")
        return
    
    # Processar XMLs
    print(f"📂 Processando XMLs em: {diretorio_xmls}")
    
    resultado = processar_diretorio_nfe_hibrido(
        diretorio_xmls,
        tabela_ncm,
        incluir_cancelamentos=True
    )
    
    # Exibir resultados
    print("\\n✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"Notas processadas: {len(resultado['notas'])}")
    print(f"Cancelamentos: {len(resultado['cancelamentos'])}")
    
    stats = resultado['estatisticas']
    print(f"Total processados: {stats['total_processados']}")
    print(f"Válidos: {stats['total_validos']}")
    print(f"Inválidos: {stats['total_invalidos']}")
    
    # Salvar resultados
    try:
        dados_serializaveis = {
            'notas': [nota.to_dict() for nota in resultado['notas']],
            'cancelamentos': [canc.to_dict() for canc in resultado['cancelamentos']],
            'estatisticas': resultado['estatisticas']
        }
        
        with open('data/resultados/resultado_rapido.json', 'w', encoding='utf-8') as f:
            json.dump(dados_serializaveis, f, indent=2, ensure_ascii=False, default=str)
        
        print("💾 Resultados salvos em: data/resultados/resultado_rapido.json")
    except Exception as e:
        print(f"⚠️  Erro ao salvar: {e}")

if __name__ == "__main__":
    import os
    main()
'''
    
    try:
        with open('uso_rapido.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("✅ uso_rapido.py")
        
        # Tornar executável no Unix
        if os.name != 'nt':
            os.chmod('uso_rapido.py', 0o755)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar script: {e}")
        return False

def exibir_instrucoes_finais():
    """Exibe instruções finais"""
    print("\n" + "=" * 50)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Coloque seus XMLs em: data/xmls/")
    print("2. Se tiver tabela NCM, coloque em: data/tabelas/")
    print("3. Execute: python uso_rapido.py")
    
    print("\n🚀 USO RÁPIDO:")
    print("```python")
    print("from parser_hibrido import processar_diretorio_nfe_hibrido")
    print("resultado = processar_diretorio_nfe_hibrido('data/xmls')")
    print("```")
    
    print("\n📖 DOCUMENTAÇÃO:")
    print("- README.md - Documentação completa")
    print("- exemplo_uso.py - Exemplos práticos")
    print("- teste_integracao.py - Testes do sistema")
    
    print("\n🔧 ARQUIVOS CRIADOS:")
    print("- config_exemplo.json - Configuração exemplo")
    print("- uso_rapido.py - Script de uso imediato")
    print("- logs/ - Diretório de logs")
    print("- data/ - Estrutura de dados")

def main():
    """Função principal do setup"""
    print("🔧 SETUP - PARSER HÍBRIDO NFE")
    print("=" * 40)
    
    # Verificações e instalações
    etapas = [
        ("Verificar Python", verificar_python),
        ("Instalar dependências", instalar_dependencias),
        ("Verificar dependências", verificar_dependencias),
        ("Testar parser", testar_parser),
        ("Criar estrutura", criar_estrutura_diretorios),
        ("Criar exemplos", criar_arquivo_exemplo),
        ("Criar script rápido", criar_script_uso_rapido)
    ]
    
    for descricao, funcao in etapas:
        if not funcao():
            print(f"\n❌ Falha na etapa: {descricao}")
            print("Setup interrompido.")
            return False
    
    # Instruções finais
    exibir_instrucoes_finais()
    return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
