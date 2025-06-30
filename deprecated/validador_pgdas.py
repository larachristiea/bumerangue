#!/usr/bin/env python3
"""
VALIDADOR DOS DADOS EXTRAÍDOS DE PGDAS
Verifica a qualidade e integridade dos JSONs gerados
"""

import os
import json
from datetime import datetime
import glob

def validar_json_pgdas(caminho_json):
    """Valida um JSON de PGDAS extraído"""
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        erros = []
        warnings = []
        
        # Validar estrutura básica
        campos_obrigatorios = [
            'arquivo_origem',
            'data_processamento', 
            'periodo_apuracao',
            'dados_estruturados'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in dados:
                erros.append(f"Campo obrigatório ausente: {campo}")
        
        # Validar dados estruturados
        if 'dados_estruturados' in dados:
            estruturados = dados['dados_estruturados']
            
            # Validar CNPJ
            cnpj = estruturados.get('cnpj', '')
            if not cnpj or len(cnpj) < 8:
                warnings.append("CNPJ não extraído ou inválido")
            
            # Validar período
            periodo = estruturados.get('periodo_apuracao', '')
            if not periodo or '/' not in periodo:
                warnings.append("Período de apuração não extraído")
            
            # Validar receita bruta
            receita_pa = estruturados.get('receita_bruta_pa', 0)
            if receita_pa <= 0:
                warnings.append("Receita bruta PA não extraída")
            
            # Validar tributos
            tributos = estruturados.get('tributos_declarados', {})
            total_tributos = tributos.get('total', 0)
            if total_tributos <= 0:
                warnings.append("Tributos não extraídos corretamente")
            
            # Validar soma dos tributos
            soma_individual = sum([
                tributos.get('pis', 0),
                tributos.get('cofins', 0),
                tributos.get('icms', 0),
                tributos.get('irpj', 0),
                tributos.get('csll', 0),
                tributos.get('cpp', 0)
            ])
            
            if abs(soma_individual - total_tributos) > 1.0:  # Tolerância de R$ 1,00
                warnings.append(f"Soma dos tributos individuais ({soma_individual:.2f}) diferente do total ({total_tributos:.2f})")
        
        return {
            'arquivo': os.path.basename(caminho_json),
            'valido': len(erros) == 0,
            'erros': erros,
            'warnings': warnings,
            'dados': dados
        }
        
    except Exception as e:
        return {
            'arquivo': os.path.basename(caminho_json),
            'valido': False,
            'erros': [f"Erro ao processar arquivo: {str(e)}"],
            'warnings': [],
            'dados': None
        }

def gerar_relatorio_validacao():
    """Gera relatório completo de validação"""
    print("🔍 VALIDADOR DE DADOS EXTRAÍDOS - PGDAS")
    print("=" * 50)
    
    base_dir = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/src/core/data/pgdas/JSON_EXTRAIDOS"
    
    if not os.path.exists(base_dir):
        print("❌ Diretório de JSONs não encontrado!")
        return
    
    # Encontrar todos os JSONs
    jsons_encontrados = glob.glob(os.path.join(base_dir, "**/*.json"), recursive=True)
    
    if not jsons_encontrados:
        print("❌ Nenhum JSON encontrado para validar!")
        return
    
    print(f"📊 Encontrados {len(jsons_encontrados)} arquivos JSON para validar\n")
    
    resultados = []
    validos = 0
    com_warnings = 0
    com_erros = 0
    
    # Validar cada arquivo
    for json_path in sorted(jsons_encontrados):
        resultado = validar_json_pgdas(json_path)
        resultados.append(resultado)
        
        if resultado['valido']:
            if len(resultado['warnings']) == 0:
                validos += 1
                print(f"✅ {resultado['arquivo']}")
            else:
                com_warnings += 1
                print(f"⚠️  {resultado['arquivo']} ({len(resultado['warnings'])} warnings)")
                for warning in resultado['warnings']:
                    print(f"   └─ {warning}")
        else:
            com_erros += 1
            print(f"❌ {resultado['arquivo']} ({len(resultado['erros'])} erros)")
            for erro in resultado['erros']:
                print(f"   └─ {erro}")
    
    # Estatísticas gerais
    print(f"\n📊 ESTATÍSTICAS DE VALIDAÇÃO:")
    print(f"   ✅ Arquivos válidos: {validos}")
    print(f"   ⚠️  Arquivos com warnings: {com_warnings}")
    print(f"   ❌ Arquivos com erros: {com_erros}")
    print(f"   📁 Total processado: {len(jsons_encontrados)}")
    
    # Análise dos dados extraídos
    print(f"\n💰 ANÁLISE DOS DADOS EXTRAÍDOS:")
    
    total_receita_pa = 0
    total_tributos = 0
    periodos_processados = set()
    cnpjs_encontrados = set()
    
    for resultado in resultados:
        if resultado['valido'] and resultado['dados']:
            dados = resultado['dados']['dados_estruturados']
            
            receita = dados.get('receita_bruta_pa', 0)
            tributos = dados.get('tributos_declarados', {}).get('total', 0)
            periodo = dados.get('periodo_apuracao', '')
            cnpj = dados.get('cnpj', '')
            
            total_receita_pa += receita
            total_tributos += tributos
            
            if periodo:
                periodos_processados.add(periodo)
            if cnpj:
                cnpjs_encontrados.add(cnpj)
    
    print(f"   💵 Total Receita Bruta PA: R$ {total_receita_pa:,.2f}")
    print(f"   📊 Total Tributos: R$ {total_tributos:,.2f}")
    print(f"   📅 Períodos únicos: {len(periodos_processados)}")
    print(f"   🏢 CNPJs únicos: {len(cnpjs_encontrados)}")
    
    if periodos_processados:
        print(f"   📆 Período mais antigo: {min(periodos_processados)}")
        print(f"   📆 Período mais recente: {max(periodos_processados)}")
    
    # Verificar completude por ano
    print(f"\n📅 COMPLETUDE POR ANO:")
    
    anos = {}
    for periodo in periodos_processados:
        if '/' in periodo:
            ano = periodo.split('/')[1]
            if ano not in anos:
                anos[ano] = []
            anos[ano].append(periodo.split('/')[0])
    
    for ano in sorted(anos.keys()):
        meses = sorted(anos[ano])
        print(f"   {ano}: {len(meses)} meses ({', '.join(meses)})")
        if len(meses) == 12:
            print(f"      ✅ Ano completo!")
        else:
            meses_faltando = set([f"{i:02d}" for i in range(1, 13)]) - set(meses)
            if meses_faltando:
                print(f"      ⚠️  Faltam: {', '.join(sorted(meses_faltando))}")
    
    # Qualidade da extração
    taxa_sucesso = (validos / len(jsons_encontrados)) * 100 if jsons_encontrados else 0
    
    print(f"\n🎯 QUALIDADE DA EXTRAÇÃO:")
    print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    if taxa_sucesso >= 95:
        print(f"   🏆 EXCELENTE! Extração de alta qualidade")
    elif taxa_sucesso >= 80:
        print(f"   👍 BOA! Extração satisfatória")
    else:
        print(f"   ⚠️  ATENÇÃO! Revisar algoritmos de extração")
    
    print(f"\n🎉 VALIDAÇÃO CONCLUÍDA!")
    
    return resultados

def main():
    """Função principal"""
    resultados = gerar_relatorio_validacao()
    
    # Salvar relatório detalhado
    relatorio_path = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/relatorio_validacao_pgdas.json"
    
    try:
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump({
                'data_validacao': datetime.now().isoformat(),
                'total_arquivos': len(resultados),
                'resultados': resultados
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório detalhado salvo em: {relatorio_path}")
    except Exception as e:
        print(f"⚠️  Erro ao salvar relatório: {str(e)}")

if __name__ == "__main__":
    main()
