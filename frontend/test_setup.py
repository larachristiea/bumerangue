#!/usr/bin/env python3
"""
Script de Teste do Frontend - Motor de Notas
Cria dados de exemplo para testar o sistema
"""

import json
import os
from datetime import datetime
from pathlib import Path

def criar_dados_exemplo():
    """Cria dados de exemplo para testar o frontend"""
    
    # Diretório base
    base_dir = Path('/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2/frontend')
    results_dir = base_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Dados de exemplo
    exemplo_resultado = {
        "periodo": "2024-03",
        "timestamp": "20240315_143022",
        "arquivos": {
            "xml_zip": "exemplo_xmls_marco_2024.zip",
            "pgdas_pdf": "exemplo_pgdas_03_2024.pdf",
            "qtd_xmls": 45
        },
        "resultados": {
            "total_monofasico": 125000.50,
            "total_nao_monofasico": 380000.75,
            "proporcao_monofasico": 24.75,
            "aliquotas": {
                "aliquota_apurada": 0.0576,
                "aliquota_pis": 0.001591,
                "aliquota_cofins": 0.007338
            },
            "tributos_recolhidos": {
                "pis": 15000.00,
                "cofins": 69000.00
            },
            "tributos_devidos": {
                "pis": 604.66,
                "cofins": 2789.23
            },
            "creditos": {
                "pis": 14395.34,
                "cofins": 66210.77,
                "total": 80606.11
            },
            "estatisticas": {
                "qtd_notas": 45,
                "qtd_itens_total": 180,
                "qtd_itens_monofasicos": 45,
                "qtd_itens_nao_monofasicos": 135
            }
        }
    }
    
    # Salvar exemplo
    exemplo_path = results_dir / 'resultado_20240315_143022.json'
    with open(exemplo_path, 'w', encoding='utf-8') as f:
        json.dump(exemplo_resultado, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dados de exemplo criados em: {exemplo_path}")
    
    # Criar mais alguns exemplos para o histórico
    exemplos_adicionais = [
        {
            "periodo": "2024-02",
            "timestamp": "20240215_091533",
            "credito_total": 67422.89,
            "qtd_xmls": 38
        },
        {
            "periodo": "2024-01",
            "timestamp": "20240115_165412",
            "credito_total": 93250.44,
            "qtd_xmls": 52
        },
        {
            "periodo": "2023-12",
            "timestamp": "20231215_102847",
            "credito_total": 71833.67,
            "qtd_xmls": 41
        }
    ]
    
    for exemplo in exemplos_adicionais:
        resultado_adicional = {
            "periodo": exemplo["periodo"],
            "timestamp": exemplo["timestamp"],
            "arquivos": {
                "xml_zip": f"xmls_{exemplo['periodo'].replace('-', '_')}.zip",
                "pgdas_pdf": f"pgdas_{exemplo['periodo'].replace('-', '_')}.pdf",
                "qtd_xmls": exemplo["qtd_xmls"]
            },
            "resultados": {
                "total_monofasico": 100000.0,
                "total_nao_monofasico": 300000.0,
                "proporcao_monofasico": 25.0,
                "aliquotas": {
                    "aliquota_apurada": 0.0576,
                    "aliquota_pis": 0.001591,
                    "aliquota_cofins": 0.007338
                },
                "tributos_recolhidos": {
                    "pis": 12000.00,
                    "cofins": 55000.00
                },
                "tributos_devidos": {
                    "pis": 500.00,
                    "cofins": 2300.00
                },
                "creditos": {
                    "pis": 11500.00,
                    "cofins": 52700.00,
                    "total": exemplo["credito_total"]
                },
                "estatisticas": {
                    "qtd_notas": exemplo["qtd_xmls"],
                    "qtd_itens_total": exemplo["qtd_xmls"] * 4,
                    "qtd_itens_monofasicos": exemplo["qtd_xmls"],
                    "qtd_itens_nao_monofasicos": exemplo["qtd_xmls"] * 3
                }
            }
        }
        
        arquivo_path = results_dir / f'resultado_{exemplo["timestamp"]}.json'
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            json.dump(resultado_adicional, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exemplo adicional criado: {arquivo_path}")

def verificar_estrutura():
    """Verifica se a estrutura do frontend está correta"""
    
    base_dir = Path('/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2/frontend')
    
    # Diretórios necessários
    dirs_necessarios = [
        'templates',
        'uploads',
        'results'
    ]
    
    # Arquivos necessários
    arquivos_necessarios = [
        'app.py',
        'start.sh',
        'frontend_requirements.txt',
        'README.md',
        'templates/base.html',
        'templates/index.html',
        'templates/dashboard.html',
        'templates/historico.html'
    ]
    
    print("🔍 Verificando estrutura do frontend...")
    
    # Verificar diretórios
    for dir_name in dirs_necessarios:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ Diretório: {dir_name}")
        else:
            print(f"❌ Diretório faltando: {dir_name}")
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Criado: {dir_name}")
    
    # Verificar arquivos
    for arquivo in arquivos_necessarios:
        arquivo_path = base_dir / arquivo
        if arquivo_path.exists():
            print(f"✅ Arquivo: {arquivo}")
        else:
            print(f"❌ Arquivo faltando: {arquivo}")

def main():
    """Função principal"""
    print("🧪 Preparando ambiente de teste para Motor de Notas Frontend")
    print("")
    
    # Verificar estrutura
    verificar_estrutura()
    print("")
    
    # Criar dados de exemplo
    print("📊 Criando dados de exemplo...")
    criar_dados_exemplo()
    print("")
    
    print("✅ Preparação concluída!")
    print("")
    print("🚀 Para testar o frontend:")
    print("   cd /Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO\\ 2/frontend")
    print("   ./start.sh")
    print("   # ou")
    print("   python app.py")
    print("")
    print("🌐 Depois acesse: http://localhost:5000")
    print("")
    print("📋 O que você pode testar:")
    print("   • Página inicial com upload")
    print("   • Histórico com dados de exemplo")
    print("   • Dashboard com métricas simuladas")
    print("   • Responsividade em diferentes tamanhos")

if __name__ == "__main__":
    main()