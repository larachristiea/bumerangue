#!/usr/bin/env python3
"""
Script de Migração - Parser Híbrido com Sistema Existente
Integra o parser híbrido robusto com as funcionalidades já existentes
"""

import os
import sys
import json
import logging
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar paths necessários
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))

# Imports do parser híbrido
from parser_hibrido import (
    NFEParserHibrido,
    processar_diretorio_nfe_hibrido,
    configurar_logging
)

# Imports do sistema existente (adaptados)
try:
    from src.tabelas import carregar_tabela_ncm_monofasico, carregar_tabela_selic
    from src.parser import carregar_pgdas  # Função existente para carregar PGDAS
except ImportError:
    print("⚠️  Módulos do sistema existente não encontrados. Usando versões simplificadas.")
    
    def carregar_tabela_ncm_monofasico():
        """Versão simplificada para teste"""
        return {}
    
    def carregar_tabela_selic():
        """Versão simplificada para teste"""
        return {}
    
    def carregar_pgdas(arquivo):
        """Versão simplificada para teste"""
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

class SistemaIntegradoNFe:
    """
    Sistema integrado que combina parser híbrido com funcionalidades existentes
    """
    
    def __init__(self, diretorio_base: str):
        self.diretorio_base = Path(diretorio_base)
        self.configurar_diretorios()
        self.configurar_logging()
        
        # Carregar tabelas de referência
        self.tabela_ncm_monofasico = self.carregar_tabelas_referencia()
        
        # Criar parser híbrido
        self.parser = NFEParserHibrido(self.tabela_ncm_monofasico)
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def configurar_diretorios(self):
        """Configura estrutura de diretórios"""
        self.dir_data = self.diretorio_base / "data"
        self.dir_xmls = self.dir_data / "xmls"
        self.dir_pgdas = self.dir_data / "pgdas"
        self.dir_tabelas = self.dir_data / "tabelas"
        self.dir_resultados = self.dir_data / "resultados"
        
        # Criar diretórios se não existirem
        for diretorio in [self.dir_data, self.dir_resultados]:
            diretorio.mkdir(exist_ok=True)
    
    def configurar_logging(self):
        """Configura logging estruturado"""
        log_file = self.diretorio_base / "logs" / f"processamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        configurar_logging("INFO", str(log_file))
    
    def carregar_tabelas_referencia(self) -> Dict:
        """Carrega tabelas de referência"""
        try:
            # Tentar carregar tabela de NCMs monofásicos
            arquivo_ncm = self.dir_tabelas / "Espelho de ncms monofásicas.json"
            if arquivo_ncm.exists():
                with open(arquivo_ncm, 'r', encoding='utf-8') as f:
                    tabela = json.load(f)
                    self.logger.info(f"Tabela NCM carregada: {len(tabela)} NCMs")
                    return tabela
            else:
                self.logger.warning("Tabela de NCMs não encontrada")
                return {}
        except Exception as e:
            self.logger.error(f"Erro ao carregar tabela NCM: {e}")
            return {}
    
    def processar_periodo(self, periodo: str) -> Dict[str, Any]:
        """
        Processa um período específico (formato: YYYY-MM)
        Integra processamento de XMLs com dados PGDAS
        """
        self.logger.info(f"Iniciando processamento do período: {periodo}")
        
        # Carregar dados PGDAS
        dados_pgdas = self.carregar_dados_pgdas(periodo)
        if not dados_pgdas:
            self.logger.error(f"Dados PGDAS não encontrados para {periodo}")
            return {"erro": "Dados PGDAS não encontrados"}
        
        # Processar XMLs do período
        resultado_xmls = self.processar_xmls_periodo(periodo)
        if not resultado_xmls['notas']:
            self.logger.warning(f"Nenhuma nota fiscal encontrada para {periodo}")
            return {"erro": "Nenhuma nota fiscal encontrada"}
        
        # Calcular créditos tributários
        resultado_creditos = self.calcular_creditos_tributarios(
            resultado_xmls['notas'], 
            dados_pgdas
        )
        
        # Consolidar resultados
        resultado_final = {
            "periodo": periodo,
            "processamento": {
                "data_hora": datetime.now().isoformat(),
                "versao_parser": "hibrido_v1.0"
            },
            "pgdas": dados_pgdas,
            "xmls": {
                "estatisticas": resultado_xmls['estatisticas'],
                "total_notas": len(resultado_xmls['notas']),
                "total_cancelamentos": len(resultado_xmls['cancelamentos'])
            },
            "creditos": resultado_creditos,
            "detalhes": {
                "notas": [nota.to_dict() for nota in resultado_xmls['notas']],
                "cancelamentos": [canc.to_dict() for canc in resultado_xmls['cancelamentos']],
                "logs": resultado_xmls['logs']
            }
        }
        
        # Salvar resultado
        self.salvar_resultado(resultado_final, periodo)
        
        # Exibir relatório
        self.gerar_relatorio_periodo(resultado_final)
        
        return resultado_final
    
    def carregar_dados_pgdas(self, periodo: str) -> Optional[Dict]:
        """Carrega dados PGDAS para o período"""
        arquivo_pgdas = self.dir_pgdas / f"{periodo}.json"
        
        if arquivo_pgdas.exists():
            try:
                with open(arquivo_pgdas, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.logger.info(f"PGDAS carregado: {periodo}")
                    return dados
            except Exception as e:
                self.logger.error(f"Erro ao carregar PGDAS {periodo}: {e}")
        else:
            self.logger.warning(f"Arquivo PGDAS não encontrado: {arquivo_pgdas}")
        
        return None
    
    def processar_xmls_periodo(self, periodo: str) -> Dict[str, Any]:
        """Processa XMLs de um período específico"""
        # Buscar diretório de XMLs do período
        possíveis_diretorios = [
            self.dir_xmls / f"{periodo}-validos",
            self.dir_xmls / f"{periodo}",
            self.dir_xmls / periodo
        ]
        
        diretorio_xmls = None
        for dir_candidato in possíveis_diretorios:
            if dir_candidato.exists():
                diretorio_xmls = dir_candidato
                break
        
        if not diretorio_xmls:
            self.logger.error(f"Diretório de XMLs não encontrado para {periodo}")
            return {"notas": [], "cancelamentos": [], "estatisticas": {}, "logs": []}
        
        self.logger.info(f"Processando XMLs do diretório: {diretorio_xmls}")
        
        # Usar parser híbrido para processar
        resultado = processar_diretorio_nfe_hibrido(
            str(diretorio_xmls),
            self.tabela_ncm_monofasico,
            incluir_cancelamentos=True
        )
        
        return resultado
    
    def calcular_creditos_tributarios(self, notas: List, dados_pgdas: Dict) -> Dict[str, Any]:
        """
        Calcula créditos tributários usando metodologia híbrida
        Combina lógica existente com validação robusta
        """
        # Totais por categoria
        total_monofasico = Decimal('0')
        total_nao_monofasico = Decimal('0')
        
        # Contadores
        itens_monofasicos = 0
        itens_nao_monofasicos = 0
        
        # Processar cada nota fiscal
        for nota in notas:
            if nota.eh_nota_cancelada():
                continue  # Pular notas canceladas
            
            for item in nota.itens:
                if not item.valido:
                    continue  # Pular itens inválidos
                
                valor_item = item.obter_valor_base_tributacao()
                
                if item.tipo_tributario == "Monofasico":
                    total_monofasico += valor_item
                    itens_monofasicos += 1
                else:
                    total_nao_monofasico += valor_item
                    itens_nao_monofasicos += 1
        
        # Calcular alíquotas efetivas
        aliquota_efetiva = Decimal(str(dados_pgdas.get("aliquota_efetiva", 0)))
        proporcoes = dados_pgdas.get("proporcoes", {})
        
        aliquota_pis = aliquota_efetiva * Decimal(str(proporcoes.get("pis", 0.0276)))
        aliquota_cofins = aliquota_efetiva * Decimal(str(proporcoes.get("cofins", 0.1274)))
        
        # Calcular tributos devidos (apenas sobre não-monofásicos)
        pis_devido = total_nao_monofasico * aliquota_pis
        cofins_devido = total_nao_monofasico * aliquota_cofins
        
        # Tributos recolhidos (do PGDAS)
        tributos = dados_pgdas.get("tributos", {})
        pis_recolhido = Decimal(str(tributos.get("pis", 0)))
        cofins_recolhido = Decimal(str(tributos.get("cofins", 0)))
        
        # Calcular créditos
        credito_pis = pis_recolhido - pis_devido
        credito_cofins = cofins_recolhido - cofins_devido
        credito_total = credito_pis + credito_cofins
        
        # Aplicar atualização SELIC (se disponível)
        credito_atualizado = self.aplicar_atualizacao_selic(credito_total, dados_pgdas.get("periodo"))
        
        return {
            "resumo": {
                "total_monofasico": float(total_monofasico),
                "total_nao_monofasico": float(total_nao_monofasico),
                "proporcao_monofasico": float((total_monofasico / (total_monofasico + total_nao_monofasico)) * 100) if (total_monofasico + total_nao_monofasico) > 0 else 0
            },
            "aliquotas": {
                "efetiva": float(aliquota_efetiva),
                "pis": float(aliquota_pis),
                "cofins": float(aliquota_cofins)
            },
            "tributos": {
                "recolhidos": {
                    "pis": float(pis_recolhido),
                    "cofins": float(cofins_recolhido),
                    "total": float(pis_recolhido + cofins_recolhido)
                },
                "devidos": {
                    "pis": float(pis_devido),
                    "cofins": float(cofins_devido),
                    "total": float(pis_devido + cofins_devido)
                }
            },
            "creditos": {
                "pis": float(credito_pis),
                "cofins": float(credito_cofins),
                "total": float(credito_total),
                "total_atualizado": float(credito_atualizado)
            },
            "estatisticas": {
                "itens_monofasicos": itens_monofasicos,
                "itens_nao_monofasicos": itens_nao_monofasicos,
                "total_itens": itens_monofasicos + itens_nao_monofasicos
            }
        }
    
    def aplicar_atualizacao_selic(self, valor: Decimal, periodo: str) -> Decimal:
        """Aplica atualização SELIC ao valor"""
        try:
            # Tentar carregar tabela SELIC
            arquivo_selic = self.dir_tabelas / "Tabela Selic.json"
            if arquivo_selic.exists():
                with open(arquivo_selic, 'r', encoding='utf-8') as f:
                    tabela_selic = json.load(f)
                
                # Calcular taxa acumulada até período atual
                taxa_acumulada = Decimal('1.0')
                for mes_data, taxa in tabela_selic.items():
                    if mes_data <= periodo:  # Simplificado
                        taxa_acumulada *= (1 + Decimal(str(taxa / 100)))
                
                return valor * taxa_acumulada
            else:
                self.logger.warning("Tabela SELIC não encontrada")
                return valor
        except Exception as e:
            self.logger.error(f"Erro ao aplicar SELIC: {e}")
            return valor
    
    def salvar_resultado(self, resultado: Dict, periodo: str):
        """Salva resultado em arquivo JSON"""
        arquivo_resultado = self.dir_resultados / f"analise_hibrida_{periodo}.json"
        
        try:
            with open(arquivo_resultado, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Resultado salvo: {arquivo_resultado}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultado: {e}")
    
    def gerar_relatorio_periodo(self, resultado: Dict):
        """Gera relatório formatado do período"""
        periodo = resultado["periodo"]
        pgdas = resultado["pgdas"]
        xmls = resultado["xmls"]
        creditos = resultado["creditos"]
        
        print("\n" + "=" * 60)
        print(f"📊 RELATÓRIO DE ANÁLISE TRIBUTÁRIA - {periodo}")
        print("=" * 60)
        
        # Dados PGDAS
        print(f"\n📋 DADOS PGDAS:")
        print(f"   CNPJ: {pgdas.get('cnpj', 'N/A')}")
        print(f"   Receita Bruta Mensal: R$ {pgdas.get('receita_bruta_mensal', 0):,.2f}")
        print(f"   Anexo: {pgdas.get('anexo', 'N/A')}")
        print(f"   Alíquota Efetiva: {pgdas.get('aliquota_efetiva', 0)*100:.2f}%")
        
        # Dados XMLs
        print(f"\n📄 DADOS NFe:")
        print(f"   Notas Processadas: {xmls['total_notas']}")
        print(f"   Cancelamentos: {xmls['total_cancelamentos']}")
        stats = xmls['estatisticas']
        print(f"   Válidas: {stats.get('total_validos', 0)}")
        print(f"   Inválidas: {stats.get('total_invalidos', 0)}")
        
        # Resumo Tributário
        resumo = creditos['resumo']
        print(f"\n💰 RESUMO TRIBUTÁRIO:")
        print(f"   Produtos Monofásicos: R$ {resumo['total_monofasico']:,.2f}")
        print(f"   Produtos Não-Monofásicos: R$ {resumo['total_nao_monofasico']:,.2f}")
        print(f"   Proporção Monofásicos: {resumo['proporcao_monofasico']:.1f}%")
        
        # Tributos
        tributos = creditos['tributos']
        print(f"\n🏛️  TRIBUTOS:")
        print(f"   PIS Recolhido: R$ {tributos['recolhidos']['pis']:,.2f}")
        print(f"   COFINS Recolhido: R$ {tributos['recolhidos']['cofins']:,.2f}")
        print(f"   PIS Devido: R$ {tributos['devidos']['pis']:,.2f}")
        print(f"   COFINS Devido: R$ {tributos['devidos']['cofins']:,.2f}")
        
        # Créditos
        cred = creditos['creditos']
        print(f"\n💎 CRÉDITOS TRIBUTÁRIOS:")
        print(f"   Crédito PIS: R$ {cred['pis']:,.2f}")
        print(f"   Crédito COFINS: R$ {cred['cofins']:,.2f}")
        print(f"   Crédito Total: R$ {cred['total']:,.2f}")
        print(f"   Crédito Atualizado SELIC: R$ {cred['total_atualizado']:,.2f}")
        
        # Estatísticas
        stats_trib = creditos['estatisticas']
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Itens Monofásicos: {stats_trib['itens_monofasicos']}")
        print(f"   Itens Não-Monofásicos: {stats_trib['itens_nao_monofasicos']}")
        print(f"   Total de Itens: {stats_trib['total_itens']}")
        
        print("\n" + "=" * 60)
        print("✅ Relatório gerado com parser híbrido robusto!")

def migrar_sistema_existente():
    """Função para migrar do sistema existente para o híbrido"""
    print("🔄 MIGRAÇÃO PARA SISTEMA HÍBRIDO")
    print("=" * 40)
    
    # Detectar diretório base
    current_dir = Path(__file__).parent.parent
    possíveis_bases = [
        current_dir,
        current_dir.parent,
        Path("/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS")
    ]
    
    diretorio_base = None
    for base in possíveis_bases:
        if (base / "data").exists() or (base / "src").exists():
            diretorio_base = base
            break
    
    if not diretorio_base:
        print("❌ Diretório base não encontrado")
        print("   Certifique-se de executar a partir do diretório correto")
        return False
    
    print(f"📁 Diretório base detectado: {diretorio_base}")
    
    # Criar sistema integrado
    try:
        sistema = SistemaIntegradoNFe(str(diretorio_base))
        print("✅ Sistema híbrido inicializado")
        
        # Detectar períodos disponíveis
        periodos = detectar_periodos_disponiveis(sistema)
        if not periodos:
            print("⚠️  Nenhum período detectado para processamento")
            return False
        
        print(f"📅 Períodos detectados: {', '.join(periodos)}")
        
        # Processar período mais recente como exemplo
        periodo_exemplo = periodos[-1]
        print(f"\n🚀 Processando período exemplo: {periodo_exemplo}")
        
        resultado = sistema.processar_periodo(periodo_exemplo)
        
        if "erro" in resultado:
            print(f"❌ Erro no processamento: {resultado['erro']}")
            return False
        
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"   Resultado salvo em: data/resultados/analise_hibrida_{periodo_exemplo}.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def detectar_periodos_disponiveis(sistema) -> List[str]:
    """Detecta períodos disponíveis para processamento"""
    periodos = []
    
    # Verificar diretórios de XMLs
    if sistema.dir_xmls.exists():
        for item in sistema.dir_xmls.iterdir():
            if item.is_dir():
                nome = item.name
                if nome.endswith("-validos"):
                    periodo = nome.replace("-validos", "")
                    if len(periodo) == 7 and "-" in periodo:  # YYYY-MM
                        periodos.append(periodo)
    
    # Verificar arquivos PGDAS
    if sistema.dir_pgdas.exists():
        for arquivo in sistema.dir_pgdas.glob("*.json"):
            nome = arquivo.stem
            if len(nome) == 7 and "-" in nome:  # YYYY-MM
                if nome not in periodos:
                    periodos.append(nome)
    
    return sorted(periodos)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema Integrado NFe Híbrido")
    parser.add_argument("--migrar", action="store_true", help="Executar migração do sistema existente")
    parser.add_argument("--periodo", type=str, help="Processar período específico (YYYY-MM)")
    
    args = parser.parse_args()
    
    if args.migrar:
        migrar_sistema_existente()
    elif args.periodo:
        diretorio_base = "/Users/mcplara/Desktop/MOTOR NOTAS ORGANIZADAS"
        sistema = SistemaIntegradoNFe(diretorio_base)
        sistema.processar_periodo(args.periodo)
    else:
        print("🚀 SISTEMA INTEGRADO NFe HÍBRIDO")
        print("Use --help para ver opções disponíveis")
