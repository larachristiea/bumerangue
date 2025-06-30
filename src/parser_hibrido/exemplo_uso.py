#!/usr/bin/env python3
"""
Exemplo de Uso do Parser Híbrido de NFe
Demonstra como usar todas as funcionalidades do parser híbrido
"""

import os
import json
import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importar o parser_hibrido
sys.path.append(str(Path(__file__).parent.parent))

from parser_hibrido import (
    NFEParserHibrido, 
    processar_xml_nfe_hibrido, 
    processar_diretorio_nfe_hibrido,
    configurar_logging,
    ValidadorFiscal
)

def exemplo_basico():
    """Exemplo básico de processamento de um XML"""
    print("=== EXEMPLO BÁSICO ===")
    
    # Configurar logging
    configurar_logging("INFO")
    
    # XML de exemplo (simplificado)
    xml_exemplo = '''<?xml version="1.0" encoding="UTF-8"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
      <NFe>
        <infNFe Id="NFe35190312345678000123550010000000011000000011" versao="4.00">
          <ide>
            <cUF>35</cUF>
            <cNF>00000011</cNF>
            <natOp>Venda</natOp>
            <mod>55</mod>
            <serie>1</serie>
            <nNF>11</nNF>
            <dhEmi>2019-03-01T10:00:00-03:00</dhEmi>
          </ide>
          <emit>
            <CNPJ>12345678000123</CNPJ>
            <xNome>Empresa Exemplo Ltda</xNome>
            <IE>123456789</IE>
          </emit>
          <det nItem="1">
            <prod>
              <cProd>001</cProd>
              <xProd>Produto A</xProd>
              <NCM>12345678</NCM>
              <CFOP>5102</CFOP>
              <qCom>10.00</qCom>
              <vUnCom>15.00</vUnCom>
              <vProd>150.00</vProd>
            </prod>
            <imposto>
              <PIS>
                <PISAliq>
                  <CST>01</CST>
                  <vBC>150.00</vBC>
                  <pPIS>1.65</pPIS>
                  <vPIS>2.48</vPIS>
                </PISAliq>
              </PIS>
              <COFINS>
                <COFINSAliq>
                  <CST>01</CST>
                  <vBC>150.00</vBC>
                  <pCOFINS>7.60</pCOFINS>
                  <vCOFINS>11.40</vCOFINS>
                </COFINSAliq>
              </COFINS>
            </imposto>
          </det>
          <total>
            <ICMSTot>
              <vProd>150.00</vProd>
              <vNF>150.00</vNF>
              <vPIS>2.48</vPIS>
              <vCOFINS>11.40</vCOFINS>
            </ICMSTot>
          </total>
        </infNFe>
      </NFe>
    </nfeProc>'''
    
    # Processar XML
    nota_fiscal = processar_xml_nfe_hibrido(xml_exemplo)
    
    if nota_fiscal:
        print(f"✅ NFe processada com sucesso!")
        print(f"   Número: {nota_fiscal.numero}")
        print(f"   Emitente: {nota_fiscal.emitente_nome}")
        print(f"   Valor total: R$ {nota_fiscal.valor_total_nf:.2f}")
        print(f"   Itens: {len(nota_fiscal.itens)}")
        print(f"   Status: {nota_fiscal.status}")
        print(f"   Válida: {nota_fiscal.valida}")
        
        # Exibir estatísticas de tributação
        stats = nota_fiscal.obter_estatisticas()
        print(f"   Itens monofásicos: {stats['itens_monofasicos']}")
        print(f"   Itens não-monofásicos: {stats['itens_nao_monofasicos']}")
    else:
        print("❌ Erro ao processar NFe")

def exemplo_com_tabela_ncm():
    """Exemplo usando tabela de NCM monofásicos"""
    print("\n=== EXEMPLO COM TABELA NCM ===")
    
    # Tabela de NCMs monofásicos (exemplo)
    tabela_ncm = {
        "12345678": {"descricao": "Produto monofásico exemplo"},
        "87654321": {"descricao": "Outro produto monofásico"},
        "11111111": {"descricao": "Terceiro produto monofásico"}
    }
    
    # Criar parser com tabela
    parser = NFEParserHibrido(tabela_ncm)
    
    print(f"Parser configurado com {len(tabela_ncm)} NCMs monofásicos")
    
    # Aqui você usaria o parser.processar_xml_nfe() com XMLs reais

def exemplo_validadores():
    """Exemplo de uso dos validadores"""
    print("\n=== EXEMPLO VALIDADORES ===")
    
    validador = ValidadorFiscal()
    
    # Testar validações
    testes = [
        ("CNPJ", "12.345.678/0001-23", validador.validar_cnpj),
        ("CPF", "123.456.789-00", validador.validar_cpf),
        ("NCM", "12345678", validador.validar_ncm),
        ("CFOP", "5102", validador.validar_cfop),
        ("CST", "01", lambda x: validador.validar_cst(x, "PIS/COFINS"))
    ]
    
    for nome, valor, func in testes:
        resultado = func(valor)
        status = "✅" if resultado else "❌"
        print(f"   {status} {nome}: {valor} -> {resultado}")
    
    # Exibir logs de validação
    logs = validador.obter_logs_validacao()
    if logs:
        print("\n   Logs de validação:")
        for log in logs[-3:]:  # Últimos 3 logs
            print(f"   {log}")

def exemplo_diretorio():
    """Exemplo de processamento de diretório"""
    print("\n=== EXEMPLO PROCESSAMENTO DIRETÓRIO ===")
    
    # Diretório de exemplo (você pode alterar para um diretório real)
    diretorio_xmls = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/xmls"
    
    if os.path.exists(diretorio_xmls):
        print(f"Processando diretório: {diretorio_xmls}")
        
        # Carregar tabela de NCMs se existir
        tabela_ncm = carregar_tabela_ncm()
        
        # Processar diretório
        resultado = processar_diretorio_nfe_hibrido(
            diretorio_xmls, 
            tabela_ncm, 
            incluir_cancelamentos=True
        )
        
        # Exibir resultados
        print(f"✅ Processamento concluído:")
        print(f"   Notas processadas: {len(resultado['notas'])}")
        print(f"   Cancelamentos: {len(resultado['cancelamentos'])}")
        
        stats = resultado['estatisticas']
        print(f"   Total processados: {stats['total_processados']}")
        print(f"   Válidos: {stats['total_validos']}")
        print(f"   Inválidos: {stats['total_invalidos']}")
        print(f"   Cancelados: {stats['total_cancelados']}")
        
        # Salvar resultados
        salvar_resultados(resultado)
        
    else:
        print(f"❌ Diretório não encontrado: {diretorio_xmls}")
        print("   Ajuste o caminho para um diretório existente com XMLs")

def carregar_tabela_ncm():
    """Carrega tabela de NCMs monofásicos"""
    try:
        # Tentar carregar tabela de NCMs existente
        caminho_tabela = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/tabelas/Espelho de ncms monofásicas.json"
        
        if os.path.exists(caminho_tabela):
            with open(caminho_tabela, 'r', encoding='utf-8') as f:
                tabela = json.load(f)
                print(f"   Tabela NCM carregada: {len(tabela)} NCMs")
                return tabela
        else:
            print("   Tabela NCM não encontrada, usando exemplo")
            return {
                "12345678": {"descricao": "Produto exemplo"},
                "87654321": {"descricao": "Outro produto exemplo"}
            }
    except Exception as e:
        print(f"   Erro ao carregar tabela NCM: {e}")
        return {}

def salvar_resultados(resultado):
    """Salva resultados do processamento"""
    try:
        # Converter para formato serializável
        dados_serializaveis = {
            'notas': [nota.to_dict() for nota in resultado['notas']],
            'cancelamentos': [canc.to_dict() for canc in resultado['cancelamentos']],
            'estatisticas': resultado['estatisticas'],
            'logs': resultado['logs']
        }
        
        # Salvar em JSON
        arquivo_resultado = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/resultado_parser_hibrido.json"
        with open(arquivo_resultado, 'w', encoding='utf-8') as f:
            json.dump(dados_serializaveis, f, indent=2, ensure_ascii=False)
        
        print(f"   Resultados salvos em: {arquivo_resultado}")
        
    except Exception as e:
        print(f"   Erro ao salvar resultados: {e}")

def exemplo_integracao_sistema_existente():
    """Exemplo de integração com sistema existente"""
    print("\n=== INTEGRAÇÃO COM SISTEMA EXISTENTE ===")
    
    # Carregar dados PGDAS (se existir)
    try:
        pgdas_path = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/pgdas/2024-12.json"
        if os.path.exists(pgdas_path):
            with open(pgdas_path, 'r', encoding='utf-8') as f:
                dados_pgdas = json.load(f)
            print(f"   PGDAS carregado: {dados_pgdas.get('periodo', 'N/A')}")
        else:
            print("   Arquivo PGDAS não encontrado")
            dados_pgdas = None
    except Exception as e:
        print(f"   Erro ao carregar PGDAS: {e}")
        dados_pgdas = None
    
    # Exemplo de cálculo de créditos (baseado no sistema existente)
    if dados_pgdas:
        print("   Exemplo de integração com cálculo de créditos disponível")
        print("   Use o resultado do parser híbrido junto com dados PGDAS")
        print("   para calcular créditos tributários")

def main():
    """Função principal com todos os exemplos"""
    print("🚀 EXEMPLOS DE USO - PARSER HÍBRIDO NFE")
    print("=" * 50)
    
    # Executar exemplos
    exemplo_basico()
    exemplo_com_tabela_ncm()
    exemplo_validadores()
    exemplo_diretorio()
    exemplo_integracao_sistema_existente()
    
    print("\n" + "=" * 50)
    print("✅ Todos os exemplos executados!")
    print("\n📖 PRÓXIMOS PASSOS:")
    print("1. Ajuste os caminhos dos diretórios para seus dados reais")
    print("2. Configure a tabela de NCMs monofásicos")
    print("3. Integre com seu sistema de cálculo de créditos")
    print("4. Use o logging para monitorar o processamento")

if __name__ == "__main__":
    main()
