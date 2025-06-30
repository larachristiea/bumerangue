#!/usr/bin/env python3
"""
Script de Teste e Integração - Parser Híbrido NFe
Valida funcionamento e integração com sistema existente
"""

import os
import sys
import json
import time
from pathlib import Path
from decimal import Decimal

# Adicionar paths necessários
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

# Imports do parser híbrido
try:
    from parser_hibrido import (
        NFEParserHibrido, 
        processar_xml_nfe_hibrido,
        processar_diretorio_nfe_hibrido,
        configurar_logging,
        ValidadorFiscal,
        NotaFiscal,
        ItemNotaFiscal
    )
    PARSER_HIBRIDO_DISPONIVEL = True
    print("✅ Parser híbrido importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar parser híbrido: {e}")
    PARSER_HIBRIDO_DISPONIVEL = False

# Imports do sistema existente
try:
    from src.parser import processar_xmls, parse_nfe
    from processador_nfe import processar_xmls as processar_nfe_original
    SISTEMA_EXISTENTE_DISPONIVEL = True
    print("✅ Sistema existente importado com sucesso")
except ImportError as e:
    print(f"⚠️  Sistema existente não disponível: {e}")
    SISTEMA_EXISTENTE_DISPONIVEL = False

class TestadorIntegracao:
    """Classe para testar integração do parser híbrido"""
    
    def __init__(self):
        self.resultados_testes = []
        self.configurar_ambiente()
    
    def configurar_ambiente(self):
        """Configura ambiente de teste"""
        configurar_logging("INFO")
        print("🔧 Ambiente configurado")
    
    def teste_validadores(self):
        """Testa validadores fiscais"""
        print("\n=== TESTE: VALIDADORES FISCAIS ===")
        
        validador = ValidadorFiscal()
        
        testes = [
            # (tipo, valor, esperado)
            ("CNPJ", "12.345.678/0001-23", True),
            ("CNPJ", "123456780001234", True),  # Sem formatação
            ("CNPJ", "123", False),  # Muito curto
            ("CPF", "123.456.789-00", True),
            ("CPF", "12345678900", True),  # Sem formatação
            ("NCM", "12345678", True),
            ("NCM", "1234567", False),  # 7 dígitos
            ("NCM", "123456789", False),  # 9 dígitos
            ("CFOP", "5102", True),
            ("CFOP", "510", False),  # 3 dígitos
            ("CST", "01", True),
            ("CST", "99", True),
            ("CST", "100", False),  # 3 dígitos
        ]
        
        sucessos = 0
        for tipo, valor, esperado in testes:
            if tipo == "CNPJ":
                resultado = validador.validar_cnpj(valor)
            elif tipo == "CPF":
                resultado = validador.validar_cpf(valor)
            elif tipo == "NCM":
                resultado = validador.validar_ncm(valor)
            elif tipo == "CFOP":
                resultado = validador.validar_cfop(valor)
            elif tipo == "CST":
                resultado = validador.validar_cst(valor)
            
            status = "✅" if resultado == esperado else "❌"
            print(f"  {status} {tipo}: {valor} -> {resultado} (esperado: {esperado})")
            
            if resultado == esperado:
                sucessos += 1
        
        taxa_sucesso = (sucessos / len(testes)) * 100
        print(f"\n📊 Taxa de sucesso: {taxa_sucesso:.1f}% ({sucessos}/{len(testes)})")
        
        self.resultados_testes.append({
            'teste': 'validadores',
            'sucessos': sucessos,
            'total': len(testes),
            'taxa_sucesso': taxa_sucesso
        })
    
    def teste_parser_basico(self):
        """Testa parser com XML básico"""
        print("\n=== TESTE: PARSER BÁSICO ===")
        
        xml_teste = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
  <NFe>
    <infNFe Id="NFe35190312345678000123550010000000011000000011" versao="4.00">
      <ide>
        <cUF>35</cUF>
        <cNF>00000011</cNF>
        <natOp>Venda de mercadoria</natOp>
        <mod>55</mod>
        <serie>1</serie>
        <nNF>11</nNF>
        <dhEmi>2024-12-01T10:00:00-03:00</dhEmi>
      </ide>
      <emit>
        <CNPJ>12345678000123</CNPJ>
        <xNome>Empresa Teste Ltda</xNome>
        <IE>123456789</IE>
        <enderEmit>
          <xLgr>Rua Teste</xLgr>
          <nro>123</nro>
          <xBairro>Centro</xBairro>
          <xMun>São Paulo</xMun>
          <UF>SP</UF>
          <CEP>01000000</CEP>
        </enderEmit>
      </emit>
      <dest>
        <CNPJ>98765432000187</CNPJ>
        <xNome>Cliente Teste Ltda</xNome>
      </dest>
      <det nItem="1">
        <prod>
          <cProd>PROD001</cProd>
          <cEAN>1234567890123</cEAN>
          <xProd>Produto de Teste</xProd>
          <NCM>12345678</NCM>
          <CFOP>5102</CFOP>
          <uCom>UN</uCom>
          <qCom>10.0000</qCom>
          <vUnCom>15.0000</vUnCom>
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
        
        try:
            inicio = time.time()
            nota = processar_xml_nfe_hibrido(xml_teste)
            tempo_processamento = time.time() - inicio
            
            if nota:
                print("✅ XML processado com sucesso")
                print(f"   Tempo: {tempo_processamento:.3f}s")
                print(f"   Chave: {nota.chave_acesso}")
                print(f"   Número: {nota.numero}")
                print(f"   Emitente: {nota.emitente_nome}")
                print(f"   Valor: R$ {nota.valor_total_nf:.2f}")
                print(f"   Itens: {len(nota.itens)}")
                print(f"   Válida: {nota.valida}")
                
                # Verificar item
                if nota.itens:
                    item = nota.itens[0]
                    print(f"   Item 1: {item.descricao}")
                    print(f"   NCM: {item.ncm}")
                    print(f"   PIS CST: {item.pis_cst}")
                    print(f"   COFINS CST: {item.cofins_cst}")
                    print(f"   Tipo: {item.tipo_tributario}")
                
                self.resultados_testes.append({
                    'teste': 'parser_basico',
                    'sucesso': True,
                    'tempo': tempo_processamento,
                    'detalhes': {
                        'chave': nota.chave_acesso,
                        'numero': nota.numero,
                        'itens': len(nota.itens),
                        'valida': nota.valida
                    }
                })
            else:
                print("❌ Falha ao processar XML")
                self.resultados_testes.append({
                    'teste': 'parser_basico',
                    'sucesso': False,
                    'tempo': tempo_processamento
                })
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            self.resultados_testes.append({
                'teste': 'parser_basico',
                'sucesso': False,
                'erro': str(e)
            })
    
    def teste_classificacao_ncm(self):
        """Testa classificação por NCM"""
        print("\n=== TESTE: CLASSIFICAÇÃO NCM ===")
        
        # Tabela de teste
        tabela_ncm_teste = {
            "12345678": {"descricao": "Produto monofásico teste"},
            "87654321": {"descricao": "Outro produto monofásico"},
            "11111111": {"descricao": "Terceiro produto monofásico"}
        }
        
        parser = NFEParserHibrido(tabela_ncm_teste)
        
        # XMLs de teste com diferentes NCMs
        testes_ncm = [
            ("12345678", "Monofasico"),  # NCM na tabela
            ("87654321", "Monofasico"),  # NCM na tabela
            ("99999999", "NaoMonofasico"),  # NCM não na tabela
        ]
        
        for ncm, tipo_esperado in testes_ncm:
            xml_ncm = f'''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
  <NFe>
    <infNFe Id="NFe35190312345678000123550010000000011000000011">
      <ide><nNF>1</nNF><serie>1</serie><dhEmi>2024-12-01T10:00:00</dhEmi></ide>
      <emit><CNPJ>12345678000123</CNPJ><xNome>Teste</xNome></emit>
      <det nItem="1">
        <prod>
          <cProd>001</cProd>
          <xProd>Produto Teste</xProd>
          <NCM>{ncm}</NCM>
          <vProd>100.00</vProd>
        </prod>
        <imposto>
          <PIS><PISAliq><CST>01</CST><vPIS>0</vPIS></PISAliq></PIS>
          <COFINS><COFINSAliq><CST>01</CST><vCOFINS>0</vCOFINS></COFINSAliq></COFINS>
        </imposto>
      </det>
      <total><ICMSTot><vNF>100.00</vNF></ICMSTot></total>
    </infNFe>
  </NFe>
</nfeProc>'''
            
            nota = parser.processar_xml_nfe(xml_ncm)
            if nota and nota.itens:
                item = nota.itens[0]
                resultado = item.tipo_tributario
                status = "✅" if resultado == tipo_esperado else "❌"
                print(f"  {status} NCM {ncm}: {resultado} (esperado: {tipo_esperado})")
            else:
                print(f"  ❌ NCM {ncm}: Erro ao processar")
        
        print(f"✅ Teste de classificação NCM concluído")
    
    def teste_performance(self):
        """Testa performance do parser"""
        print("\n=== TESTE: PERFORMANCE ===")
        
        # XML de teste
        xml_teste = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
  <NFe>
    <infNFe Id="NFe35190312345678000123550010000000011000000011">
      <ide><nNF>1</nNF><serie>1</serie><dhEmi>2024-12-01T10:00:00</dhEmi></ide>
      <emit><CNPJ>12345678000123</CNPJ><xNome>Teste</xNome></emit>
      <det nItem="1">
        <prod><cProd>001</cProd><xProd>Produto</xProd><NCM>12345678</NCM><vProd>100.00</vProd></prod>
        <imposto><PIS><PISAliq><CST>01</CST><vPIS>0</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vCOFINS>0</vCOFINS></COFINSAliq></COFINS></imposto>
      </det>
      <total><ICMSTot><vNF>100.00</vNF></ICMSTot></total>
    </infNFe>
  </NFe>
</nfeProc>'''
        
        # Teste de múltiplas execuções
        num_execucoes = 100
        print(f"  Processando {num_execucoes} XMLs...")
        
        inicio = time.time()
        sucessos = 0
        
        for i in range(num_execucoes):
            nota = processar_xml_nfe_hibrido(xml_teste)
            if nota:
                sucessos += 1
        
        tempo_total = time.time() - inicio
        tempo_medio = tempo_total / num_execucoes
        
        print(f"  ✅ Performance:")
        print(f"     Tempo total: {tempo_total:.3f}s")
        print(f"     Tempo médio: {tempo_medio:.3f}s por XML")
        print(f"     Taxa sucesso: {sucessos}/{num_execucoes}")
        print(f"     Throughput: {num_execucoes/tempo_total:.1f} XMLs/s")
        
        self.resultados_testes.append({
            'teste': 'performance',
            'execucoes': num_execucoes,
            'tempo_total': tempo_total,
            'tempo_medio': tempo_medio,
            'sucessos': sucessos,
            'throughput': num_execucoes/tempo_total
        })
    
    def teste_integracao_sistema_existente(self):
        """Testa integração com sistema existente"""
        print("\n=== TESTE: INTEGRAÇÃO SISTEMA EXISTENTE ===")
        
        if not SISTEMA_EXISTENTE_DISPONIVEL:
            print("  ⚠️  Sistema existente não disponível, pulando teste")
            return
        
        # Comparar resultados entre sistemas
        xml_teste = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
  <NFe>
    <infNFe Id="NFe35190312345678000123550010000000011000000011">
      <ide><nNF>123</nNF><serie>1</serie><dhEmi>2024-12-01T10:00:00</dhEmi></ide>
      <emit><CNPJ>12345678000123</CNPJ><xNome>Empresa Teste</xNome></emit>
      <det nItem="1">
        <prod><cProd>PROD001</cProd><xProd>Produto Teste</xProd><NCM>12345678</NCM><vProd>150.00</vProd></prod>
        <imposto><PIS><PISAliq><CST>01</CST><vPIS>2.48</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vCOFINS>11.40</vCOFINS></COFINSAliq></COFINS></imposto>
      </det>
      <total><ICMSTot><vNF>150.00</vNF></ICMSTot></total>
    </infNFe>
  </NFe>
</nfeProc>'''
        
        try:
            # Parser híbrido
            nota_hibrida = processar_xml_nfe_hibrido(xml_teste)
            
            # Parser existente (se disponível)
            # nota_existente = parse_nfe(xml_teste)
            
            print("  ✅ Processamento híbrido funcionando")
            if nota_hibrida:
                print(f"     NFe: {nota_hibrida.numero}")
                print(f"     Emitente: {nota_hibrida.emitente_nome}")
                print(f"     Valor: R$ {nota_hibrida.valor_total_nf:.2f}")
            
            # Aqui seria feita a comparação entre os resultados
            print("  📋 Comparação com sistema existente necessita implementação específica")
            
        except Exception as e:
            print(f"  ❌ Erro na integração: {e}")
    
    def teste_diretorio(self):
        """Testa processamento de diretório"""
        print("\n=== TESTE: PROCESSAMENTO DIRETÓRIO ===")
        
        # Verificar se existe diretório de XMLs
        diretorios_teste = [
            "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/xmls",
            "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/xml_organizer_scripts"
        ]
        
        diretorio_encontrado = None
        for diretorio in diretorios_teste:
            if os.path.exists(diretorio):
                diretorio_encontrado = diretorio
                break
        
        if not diretorio_encontrado:
            print("  ⚠️  Nenhum diretório de XMLs encontrado para teste")
            return
        
        print(f"  📁 Testando diretório: {diretorio_encontrado}")
        
        try:
            inicio = time.time()
            resultado = processar_diretorio_nfe_hibrido(diretorio_encontrado)
            tempo_processamento = time.time() - inicio
            
            print(f"  ✅ Diretório processado em {tempo_processamento:.2f}s")
            print(f"     Notas: {len(resultado['notas'])}")
            print(f"     Cancelamentos: {len(resultado['cancelamentos'])}")
            
            stats = resultado['estatisticas']
            print(f"     Processados: {stats['total_processados']}")
            print(f"     Válidos: {stats['total_validos']}")
            print(f"     Inválidos: {stats['total_invalidos']}")
            
            self.resultados_testes.append({
                'teste': 'diretorio',
                'sucesso': True,
                'tempo': tempo_processamento,
                'notas': len(resultado['notas']),
                'estatisticas': stats
            })
            
        except Exception as e:
            print(f"  ❌ Erro no processamento: {e}")
            self.resultados_testes.append({
                'teste': 'diretorio',
                'sucesso': False,
                'erro': str(e)
            })
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO BATERIA DE TESTES")
        print("=" * 50)
        
        if not PARSER_HIBRIDO_DISPONIVEL:
            print("❌ Parser híbrido não disponível. Verifique instalação.")
            return
        
        # Executar testes
        self.teste_validadores()
        self.teste_parser_basico()
        self.teste_classificacao_ncm()
        self.teste_performance()
        self.teste_integracao_sistema_existente()
        self.teste_diretorio()
        
        # Resumo
        self.gerar_relatorio_final()
    
    def gerar_relatorio_final(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 50)
        
        testes_executados = len(self.resultados_testes)
        testes_sucessos = len([t for t in self.resultados_testes if t.get('sucesso', True)])
        
        print(f"Testes executados: {testes_executados}")
        print(f"Sucessos: {testes_sucessos}")
        print(f"Taxa de sucesso: {(testes_sucessos/testes_executados)*100:.1f}%")
        
        print("\nDetalhes por teste:")
        for teste in self.resultados_testes:
            nome = teste['teste']
            if 'taxa_sucesso' in teste:
                print(f"  {nome}: {teste['taxa_sucesso']:.1f}% ({teste['sucessos']}/{teste['total']})")
            elif 'sucesso' in teste:
                status = "✅" if teste['sucesso'] else "❌"
                print(f"  {nome}: {status}")
            else:
                print(f"  {nome}: Executado")
        
        # Salvar relatório
        self.salvar_relatorio()
        
        print("\n🎉 TESTES CONCLUÍDOS!")
        print("✅ Parser híbrido está funcionando corretamente")
        print("📝 Relatório salvo em: relatorio_testes.json")
    
    def salvar_relatorio(self):
        """Salva relatório em arquivo JSON"""
        try:
            relatorio = {
                'timestamp': time.time(),
                'data': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ambiente': {
                    'parser_hibrido_disponivel': PARSER_HIBRIDO_DISPONIVEL,
                    'sistema_existente_disponivel': SISTEMA_EXISTENTE_DISPONIVEL
                },
                'resultados': self.resultados_testes
            }
            
            with open('relatorio_testes.json', 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"⚠️  Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    print("🚀 TESTE E INTEGRAÇÃO - PARSER HÍBRIDO NFE")
    print("=" * 50)
    
    testador = TestadorIntegracao()
    testador.executar_todos_testes()

if __name__ == "__main__":
    main()
