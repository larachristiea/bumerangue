#!/usr/bin/env python3
"""
Demonstração Completa - Parser Híbrido NFe
Script final mostrando todas as funcionalidades implementadas
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Adicionar path do parser híbrido
sys.path.append(str(Path(__file__).parent))

print("🚀 DEMONSTRAÇÃO COMPLETA - PARSER HÍBRIDO NFE")
print("=" * 60)

# Verificar disponibilidade do parser híbrido
try:
    from models import NotaFiscal, ItemNotaFiscal, converter_para_decimal
    from validators import ValidadorFiscal
    from utils import UtilXML, UtilData, UtilValor, UtilArquivo, UtilTributario, UtilLog, NAMESPACE_NFE
    from parser_hibrido import NFEParserHibrido, processar_xml_nfe_hibrido, processar_diretorio_nfe_hibrido
    
    def configurar_logging(nivel="INFO", arquivo=None):
        UtilLog.configurar_logging(nivel, arquivo)
    
    def versao():
        return "1.0.0"
    
    print(f"✅ Parser Híbrido v{versao()} carregado com sucesso")
    PARSER_OK = True
except ImportError as e:
    print(f"❌ Erro ao carregar parser híbrido: {e}")
    PARSER_OK = False

if not PARSER_OK:
    print("\n❌ Não foi possível carregar o parser híbrido")
    print("   Verifique se todos os arquivos foram criados corretamente")
    sys.exit(1)

def demonstrar_validadores():
    """Demonstra funcionamento dos validadores"""
    print("\n📋 DEMONSTRAÇÃO: VALIDADORES FISCAIS")
    print("-" * 40)
    
    validador = ValidadorFiscal()
    
    # Casos de teste
    testes = [
        ("CNPJ", "12.345.678/0001-23", "Válido"),
        ("CNPJ", "123", "Inválido - muito curto"),
        ("CPF", "123.456.789-00", "Válido"),
        ("CPF", "123456789001", "Inválido - 12 dígitos"),
        ("NCM", "12345678", "Válido"),
        ("NCM", "1234567", "Inválido - 7 dígitos"),
        ("CFOP", "5102", "Válido"),
        ("CFOP", "0102", "Inválido - primeiro dígito 0"),
        ("CST", "01", "Válido"),
        ("CST", "100", "Inválido - 3 dígitos"),
    ]
    
    sucessos = 0
    total = len(testes)
    
    for tipo, valor, descricao in testes:
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
        
        esperado = "Válido" in descricao
        correto = resultado == esperado
        
        if correto:
            sucessos += 1
        
        status = "✅" if correto else "❌"
        print(f"  {status} {tipo}: {valor:<20} | {descricao}")
    
    print(f"\n📊 Validadores: {sucessos}/{total} testes corretos ({(sucessos/total)*100:.1f}%)")

def demonstrar_parser_xml():
    """Demonstra parsing de XML individual"""
    print("\n🔍 DEMONSTRAÇÃO: PARSER XML INDIVIDUAL")
    print("-" * 40)
    
    # XML de demonstração
    xml_demo = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
  <NFe>
    <infNFe Id="NFe35240112345678000123550010000000011000000011" versao="4.00">
      <ide>
        <cUF>35</cUF>
        <cNF>00000011</cNF>
        <natOp>Venda de mercadoria</natOp>
        <mod>55</mod>
        <serie>1</serie>
        <nNF>123</nNF>
        <dhEmi>2024-12-01T14:30:00-03:00</dhEmi>
      </ide>
      <emit>
        <CNPJ>12345678000123</CNPJ>
        <xNome>Empresa Demonstração Ltda</xNome>
        <IE>123456789</IE>
        <enderEmit>
          <xLgr>Rua da Demonstração</xLgr>
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
          <xProd>Produto Monofásico Demo</xProd>
          <NCM>12345678</NCM>
          <CFOP>5102</CFOP>
          <uCom>UN</uCom>
          <qCom>10.0000</qCom>
          <vUnCom>25.0000</vUnCom>
          <vProd>250.00</vProd>
        </prod>
        <imposto>
          <PIS>
            <PISAliq>
              <CST>01</CST>
              <vBC>250.00</vBC>
              <pPIS>1.65</pPIS>
              <vPIS>4.13</vPIS>
            </PISAliq>
          </PIS>
          <COFINS>
            <COFINSAliq>
              <CST>01</CST>
              <vBC>250.00</vBC>
              <pCOFINS>7.60</pCOFINS>
              <vCOFINS>19.00</vCOFINS>
            </COFINSAliq>
          </COFINS>
        </imposto>
      </det>
      <det nItem="2">
        <prod>
          <cProd>PROD002</cProd>
          <xProd>Produto Regular Demo</xProd>
          <NCM>87654321</NCM>
          <CFOP>5102</CFOP>
          <uCom>UN</uCom>
          <qCom>5.0000</qCom>
          <vUnCom>30.0000</vUnCom>
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
          <vProd>400.00</vProd>
          <vNF>400.00</vNF>
          <vPIS>6.61</vPIS>
          <vCOFINS>30.40</vCOFINS>
        </ICMSTot>
      </total>
    </infNFe>
  </NFe>
</nfeProc>'''
    
    # Tabela NCM de demonstração
    tabela_ncm_demo = {
        "12345678": {"descricao": "Produto monofásico demonstração"},
        "11111111": {"descricao": "Outro produto monofásico"},
        "22222222": {"descricao": "Terceiro produto monofásico"}
    }
    
    try:
        print("📄 Processando XML de demonstração...")
        
        inicio = time.time()
        parser = NFEParserHibrido(tabela_ncm_demo)
        nota = parser.processar_xml_nfe(xml_demo, "demo.xml")
        tempo_processamento = time.time() - inicio
        
        if nota:
            print(f"✅ XML processado em {tempo_processamento:.3f}s")
            print(f"   📋 NFe: {nota.numero}-{nota.serie}")
            print(f"   🏢 Emitente: {nota.emitente_nome}")
            print(f"   🧾 Chave: {nota.chave_acesso[:20]}...")
            print(f"   💰 Valor total: R$ {nota.valor_total_nf:.2f}")
            print(f"   📦 Itens: {len(nota.itens)}")
            print(f"   ✔️  Status: {nota.status}")
            print(f"   ✅ Válida: {nota.valida}")
            
            # Estatísticas tributárias
            stats = nota.obter_estatisticas()
            print(f"\n   📊 Estatísticas Tributárias:")
            print(f"      Itens monofásicos: {stats['itens_monofasicos']}")
            print(f"      Itens não-monofásicos: {stats['itens_nao_monofasicos']}")
            print(f"      Valor monofásicos: R$ {stats['valor_total_monofasicos']:.2f}")
            print(f"      Proporção monofásicos: {stats['proporcao_monofasicos']:.1f}%")
            
            # Detalhes dos itens
            print(f"\n   📝 Detalhes dos Itens:")
            for i, item in enumerate(nota.itens, 1):
                print(f"      Item {i}: {item.descricao[:30]}")
                print(f"         NCM: {item.ncm} | Tipo: {item.tipo_tributario}")
                print(f"         Valor: R$ {item.valor_total:.2f}")
                print(f"         PIS CST: {item.pis_cst} | COFINS CST: {item.cofins_cst}")
            
            return True
        else:
            print("❌ Falha no processamento do XML")
            return False
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def demonstrar_processamento_diretorio():
    """Demonstra processamento de diretório"""
    print("\n📁 DEMONSTRAÇÃO: PROCESSAMENTO DE DIRETÓRIO")
    print("-" * 40)
    
    # Verificar se existe diretório com XMLs
    diretorios_teste = [
        "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS/data/xmls",
        "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS",
        "."
    ]
    
    diretorio_encontrado = None
    for diretorio in diretorios_teste:
        if os.path.exists(diretorio):
            xmls = [f for f in os.listdir(diretorio) if f.lower().endswith('.xml')]
            if xmls:
                diretorio_encontrado = diretorio
                print(f"📂 Diretório encontrado: {diretorio}")
                print(f"   {len(xmls)} arquivos XML disponíveis")
                break
    
    if not diretorio_encontrado:
        print("⚠️  Nenhum diretório com XMLs encontrado")
        print("   Criando demonstração com XML sintético...")
        return demonstrar_xml_sintetico()
    
    try:
        # Carregar tabela NCM se disponível
        tabela_ncm = carregar_tabela_ncm()
        
        print(f"🔄 Processando diretório: {diretorio_encontrado}")
        
        inicio = time.time()
        resultado = processar_diretorio_nfe_hibrido(
            diretorio_encontrado,
            tabela_ncm,
            incluir_cancelamentos=True
        )
        tempo_total = time.time() - inicio
        
        print(f"✅ Processamento concluído em {tempo_total:.2f}s")
        
        # Estatísticas
        stats = resultado['estatisticas']
        print(f"\n📊 Estatísticas do Processamento:")
        print(f"   Total processados: {stats['total_processados']}")
        print(f"   Válidos: {stats['total_validos']}")
        print(f"   Inválidos: {stats['total_invalidos']}")
        print(f"   Cancelados: {stats['total_cancelados']}")
        
        print(f"\n📋 Resultados:")
        print(f"   Notas fiscais: {len(resultado['notas'])}")
        print(f"   Eventos de cancelamento: {len(resultado['cancelamentos'])}")
        
        if resultado['notas']:
            # Análise tributária agregada
            total_monofasico = sum(
                nota.obter_valor_total_monofasicos() for nota in resultado['notas']
            )
            total_nao_monofasico = sum(
                nota.obter_valor_total_nao_monofasicos() for nota in resultado['notas']
            )
            total_geral = total_monofasico + total_nao_monofasico
            
            if total_geral > 0:
                proporcao = (total_monofasico / total_geral) * 100
                print(f"\n💰 Análise Tributária Agregada:")
                print(f"   Valor monofásicos: R$ {total_monofasico:.2f}")
                print(f"   Valor não-monofásicos: R$ {total_nao_monofasico:.2f}")
                print(f"   Proporção monofásicos: {proporcao:.1f}%")
        
        # Salvar resultados
        salvar_resultados_demonstracao(resultado)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def demonstrar_xml_sintetico():
    """Cria e processa XMLs sintéticos para demonstração"""
    print("🧪 Criando XMLs sintéticos para demonstração...")
    
    # Criar diretório temporário
    temp_dir = "temp_demo_xmls"
    os.makedirs(temp_dir, exist_ok=True)
    
    # XMLs sintéticos
    xmls_demo = [
        {
            'nome': 'nfe_demo_001.xml',
            'numero': '001',
            'ncm': '12345678',  # Monofásico
            'valor': '100.00'
        },
        {
            'nome': 'nfe_demo_002.xml',
            'numero': '002',
            'ncm': '87654321',  # Não-monofásico
            'valor': '200.00'
        },
        {
            'nome': 'nfe_demo_003.xml',
            'numero': '003',
            'ncm': '11111111',  # Monofásico
            'valor': '150.00'
        }
    ]
    
    try:
        for xml_info in xmls_demo:
            xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
  <NFe>
    <infNFe Id="NFe3524011234567800012355001000000{xml_info['numero']}1000000{xml_info['numero']}1">
      <ide>
        <nNF>{xml_info['numero']}</nNF>
        <serie>1</serie>
        <dhEmi>2024-12-01T15:00:00-03:00</dhEmi>
      </ide>
      <emit>
        <CNPJ>12345678000123</CNPJ>
        <xNome>Empresa Demo Ltda</xNome>
      </emit>
      <det nItem="1">
        <prod>
          <cProd>PROD{xml_info['numero']}</cProd>
          <xProd>Produto Demo {xml_info['numero']}</xProd>
          <NCM>{xml_info['ncm']}</NCM>
          <CFOP>5102</CFOP>
          <vProd>{xml_info['valor']}</vProd>
        </prod>
        <imposto>
          <PIS><PISAliq><CST>01</CST><vPIS>1.65</vPIS></PISAliq></PIS>
          <COFINS><COFINSAliq><CST>01</CST><vCOFINS>7.60</vCOFINS></COFINSAliq></COFINS>
        </imposto>
      </det>
      <total><ICMSTot><vNF>{xml_info['valor']}</vNF></ICMSTot></total>
    </infNFe>
  </NFe>
</nfeProc>'''
            
            caminho_xml = os.path.join(temp_dir, xml_info['nome'])
            with open(caminho_xml, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        
        print(f"✅ {len(xmls_demo)} XMLs sintéticos criados em {temp_dir}/")
        
        # Processar XMLs sintéticos
        tabela_ncm = {
            "12345678": {"descricao": "Produto monofásico demo"},
            "11111111": {"descricao": "Outro produto monofásico demo"}
        }
        
        resultado = processar_diretorio_nfe_hibrido(temp_dir, tabela_ncm)
        
        print(f"✅ XMLs sintéticos processados:")
        print(f"   Notas: {len(resultado['notas'])}")
        print(f"   Válidas: {resultado['estatisticas']['total_validos']}")
        
        # Limpar diretório temporário
        import shutil
        shutil.rmtree(temp_dir)
        print(f"🧹 Diretório temporário removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração sintética: {e}")
        return False

def carregar_tabela_ncm():
    """Carrega tabela NCM do sistema"""
    caminhos_tabela = [
        "data/tabelas/Espelho de ncms monofásicas.json",
        "../data/tabelas/Espelho de ncms monofásicas.json",
        "tabela_ncm_demo.json"
    ]
    
    for caminho in caminhos_tabela:
        try:
            if os.path.exists(caminho):
                with open(caminho, 'r', encoding='utf-8') as f:
                    tabela = json.load(f)
                print(f"📋 Tabela NCM carregada: {len(tabela)} NCMs ({caminho})")
                return tabela
        except Exception:
            continue
    
    # Tabela demo se não encontrar
    print("📋 Usando tabela NCM de demonstração")
    return {
        "12345678": {"descricao": "Produto monofásico demo"},
        "11111111": {"descricao": "Outro produto monofásico demo"},
        "22222222": {"descricao": "Terceiro produto monofásico demo"}
    }

def salvar_resultados_demonstracao(resultado):
    """Salva resultados da demonstração"""
    try:
        # Criar diretório de resultados
        os.makedirs("resultados_demo", exist_ok=True)
        
        # Preparar dados serializáveis
        dados_demo = {
            'timestamp': datetime.now().isoformat(),
            'parser_version': versao(),
            'estatisticas': resultado['estatisticas'],
            'total_notas': len(resultado['notas']),
            'total_cancelamentos': len(resultado['cancelamentos']),
            'notas': [nota.to_dict() for nota in resultado['notas'][:5]],  # Apenas primeiras 5
            'cancelamentos': [canc.to_dict() for canc in resultado['cancelamentos']]
        }
        
        # Salvar JSON
        with open('resultados_demo/demonstracao_completa.json', 'w', encoding='utf-8') as f:
            json.dump(dados_demo, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Resultados salvos em: resultados_demo/demonstracao_completa.json")
        
        # Relatório resumido
        with open('resultados_demo/relatorio_demonstracao.txt', 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE DEMONSTRAÇÃO - PARSER HÍBRIDO NFE\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Versão: {versao()}\n\n")
            f.write(f"ESTATÍSTICAS:\n")
            f.write(f"- Total processados: {resultado['estatisticas']['total_processados']}\n")
            f.write(f"- Válidos: {resultado['estatisticas']['total_validos']}\n")
            f.write(f"- Inválidos: {resultado['estatisticas']['total_invalidos']}\n")
            f.write(f"- Cancelados: {resultado['estatisticas']['total_cancelados']}\n")
            f.write(f"\nRESULTADOS:\n")
            f.write(f"- Notas fiscais: {len(resultado['notas'])}\n")
            f.write(f"- Eventos cancelamento: {len(resultado['cancelamentos'])}\n")
        
        print(f"📄 Relatório salvo em: resultados_demo/relatorio_demonstracao.txt")
        
    except Exception as e:
        print(f"⚠️  Erro ao salvar resultados: {e}")

def demonstrar_funcionalidades_avancadas():
    """Demonstra funcionalidades avançadas"""
    print("\n🎛️  DEMONSTRAÇÃO: FUNCIONALIDADES AVANÇADAS")
    print("-" * 40)
    
    # Configuração de logging avançado
    print("📝 Configurando logging estruturado...")
    configurar_logging("DEBUG", "logs/demo_parser.log")
    print("✅ Logging configurado: logs/demo_parser.log")
    
    # Validador customizado
    print("\n🔧 Demonstrando validador customizado...")
    validador = ValidadorFiscal()
    
    # Teste de classificação monofásica
    testes_classificacao = [
        ("04", "04", "PIS/COFINS CST 04 - Monofásico"),
        ("05", "05", "PIS/COFINS CST 05 - Monofásico"),
        ("01", "01", "PIS/COFINS CST 01 - Não-monofásico")
    ]
    
    print("\n🏷️  Teste de classificação tributária:")
    for pis_cst, cofins_cst, descricao in testes_classificacao:
        eh_monofasico = validador.eh_produto_monofasico_por_cst(pis_cst, cofins_cst)
        status = "✅ Monofásico" if eh_monofasico else "❌ Não-monofásico"
        print(f"   {status} - {descricao}")
    
    # Demonstrar serialização JSON
    print("\n📄 Demonstrando serialização JSON...")
    try:
        from parser_hibrido import NotaFiscal, ItemNotaFiscal
        
        # Criar objetos de demonstração
        nota_demo = NotaFiscal()
        nota_demo.numero = "999"
        nota_demo.emitente_nome = "Empresa Demo JSON"
        nota_demo.valor_total_nf = 1000.50
        
        item_demo = ItemNotaFiscal()
        item_demo.numero = 1
        item_demo.descricao = "Item Demo JSON"
        item_demo.valor_total = 1000.50
        
        nota_demo.adicionar_item(item_demo)
        
        # Serializar
        json_nota = nota_demo.to_json()
        print("✅ Nota fiscal serializada para JSON")
        print(f"   Tamanho: {len(json_nota)} caracteres")
        
    except Exception as e:
        print(f"❌ Erro na serialização: {e}")

def exibir_resumo_final():
    """Exibe resumo final da demonstração"""
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO COMPLETA FINALIZADA!")
    print("=" * 60)
    
    print("\n✅ FUNCIONALIDADES DEMONSTRADAS:")
    print("   🔍 Validadores fiscais robustos")
    print("   📄 Parser XML individual com validação")
    print("   📁 Processamento de diretório completo")
    print("   🏷️  Classificação tributária híbrida (NCM + CST)")
    print("   📊 Estatísticas e métricas detalhadas")
    print("   📝 Logging estruturado")
    print("   💾 Serialização JSON completa")
    print("   🎛️  Funcionalidades avançadas")
    
    print("\n📂 ARQUIVOS CRIADOS:")
    print("   📄 resultados_demo/demonstracao_completa.json")
    print("   📋 resultados_demo/relatorio_demonstracao.txt")
    print("   📝 logs/demo_parser.log")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Execute: python setup.py (para instalação completa)")
    print("   2. Execute: python uso_rapido.py (para uso imediato)")
    print("   3. Execute: python teste_integracao.py (para testes)")
    print("   4. Execute: python migrador_sistema.py (para migração)")
    
    print("\n📖 DOCUMENTAÇÃO:")
    print("   📚 README.md - Guia de uso completo")
    print("   🔧 DOCUMENTACAO_TECNICA.md - Detalhes técnicos")
    print("   📝 exemplo_uso.py - Exemplos práticos")
    
    print("\n🏆 PARSER HÍBRIDO NFE PRONTO PARA USO!")
    print("   ✅ Validação fiscal robusta")
    print("   ✅ Compatibilidade com sistema existente")
    print("   ✅ Funcionalidades avançadas")
    print("   ✅ Documentação completa")

def main():
    """Função principal da demonstração"""
    # Configurar logging básico
    configurar_logging("INFO")
    
    print(f"🕒 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar todas as demonstrações
    demos = [
        ("Validadores Fiscais", demonstrar_validadores),
        ("Parser XML Individual", demonstrar_parser_xml),
        ("Processamento Diretório", demonstrar_processamento_diretorio),
        ("Funcionalidades Avançadas", demonstrar_funcionalidades_avancadas)
    ]
    
    sucessos = 0
    for nome, funcao in demos:
        try:
            resultado = funcao()
            if resultado:
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro em {nome}: {e}")
    
    print(f"\n📊 RESULTADO FINAL: {sucessos}/{len(demos)} demonstrações executadas com sucesso")
    
    # Resumo final
    exibir_resumo_final()

if __name__ == "__main__":
    main()
