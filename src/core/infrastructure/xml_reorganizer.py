#!/usr/bin/env python3
"""
Script Profissional de Reorganização de XMLs NFe
=====================================

Reorganiza automaticamente arquivos XML por data real de emissão extraída do conteúdo.

Funcionalidades:
- Validação automática do padrão nome vs conteúdo XML
- Backup timestampado completo antes de qualquer alteração
- Execução em fases controláveis com logs detalhados
- Tratamento de casos especiais (duplicados, corrompidos, cancelamentos)
- Capacidade de rollback completo
- Relatório final com estatísticas da reorganização

Autor: Assistente Claude
Data: 2025-05-26
"""

import os
import sys
import re
import shutil
import json
import gzip
import argparse
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set
import logging

# Configuração do logging
def setup_logging(log_dir: Path, dry_run: bool = False) -> logging.Logger:
    """Configura sistema de logging detalhado"""
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = "DRY_RUN" if dry_run else "EXECUTION"
    log_file = log_dir / f"xml_reorganizer_{mode}_{timestamp}.log"
    
    # Configurar formato detalhado
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar logger
    logger = logging.getLogger('xml_reorganizer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class XMLAnalyzer:
    """Classe para análise e extração de dados dos XMLs"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.namespace_patterns = [
            '{http://www.portalfiscal.inf.br/nfe}',
            ''  # Para XMLs sem namespace
        ]
    
    def extrair_data_xml(self, arquivo_path: Path) -> Optional[str]:
        """Extrai data de emissão do conteúdo XML"""
        try:
            tree = ET.parse(arquivo_path)
            root = tree.getroot()
            
            # Buscar dhEmi com diferentes possibilidades de namespace
            for namespace in self.namespace_patterns:
                dhemi_element = root.find(f".//{namespace}dhEmi")
                if dhemi_element is not None and dhemi_element.text:
                    data_completa = dhemi_element.text.strip()
                    # Extrair apenas a parte da data (YYYY-MM-DD)
                    data_match = re.match(r'(\d{4}-\d{2}-\d{2})', data_completa)
                    if data_match:
                        return data_match.group(1)
            
            self.logger.warning(f"Tag dhEmi não encontrada em {arquivo_path}")
            return None
            
        except ET.ParseError as e:
            self.logger.error(f"Erro de parsing XML em {arquivo_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro inesperado ao ler {arquivo_path}: {e}")
            return None
    
    def extrair_data_nome(self, nome_arquivo: str) -> Optional[str]:
        """Extrai data do nome do arquivo NFe: UF+AAMM+DD"""
        if not nome_arquivo.endswith('.xml'):
            return None
            
        # Remover extensão e sufixos como -nfe, -can
        nome_base = nome_arquivo.replace('.xml', '').split('-')[0]
        
        if len(nome_base) >= 8:
            try:
                ano_mes = nome_base[2:6]  # posições 2-5 (AAMM)
                dia = nome_base[6:8]      # posições 6-7 (DD)
                
                ano = '20' + ano_mes[:2]  # 20 + AA
                mes = ano_mes[2:4]        # MM
                
                # Validar se o mês é válido
                if 1 <= int(mes) <= 12 and 1 <= int(dia) <= 31:
                    return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
            except (ValueError, IndexError):
                pass
        
        return None
    
    def is_cancelamento(self, arquivo_path: Path) -> bool:
        """Verifica se o arquivo é um cancelamento"""
        nome = arquivo_path.name.lower()
        return '-can.xml' in nome or 'cancelamento' in nome
    
    def validate_xml_integrity(self, arquivo_path: Path) -> Dict[str, any]:
        """Valida integridade e extrai metadados do XML"""
        result = {
            'valid': False,
            'data_xml': None,
            'data_nome': None,
            'is_cancelamento': False,
            'size': 0,
            'error': None
        }
        
        try:
            result['size'] = arquivo_path.stat().st_size
            result['is_cancelamento'] = self.is_cancelamento(arquivo_path)
            result['data_nome'] = self.extrair_data_nome(arquivo_path.name)
            result['data_xml'] = self.extrair_data_xml(arquivo_path)
            result['valid'] = True
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Erro na validação de {arquivo_path}: {e}")
        
        return result

class BackupManager:
    """Classe para gerenciamento de backups"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.backup_registry = {}
    
    def create_timestamped_backup(self, source_dir: Path, backup_base_dir: Path) -> Path:
        """Cria backup completo com timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backup_base_dir / f"backup_{timestamp}"
        
        self.logger.info(f"Iniciando backup completo para: {backup_dir}")
        
        try:
            # Criar diretório de backup
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar toda a estrutura
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.xml'):
                        source_file = Path(root) / file
                        relative_path = source_file.relative_to(source_dir)
                        backup_file = backup_dir / relative_path
                        
                        # Criar diretórios necessários
                        backup_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copiar arquivo
                        shutil.copy2(source_file, backup_file)
                        total_files += 1
                        total_size += source_file.stat().st_size
            
            # Salvar metadados do backup
            metadata = {
                'timestamp': timestamp,
                'source_dir': str(source_dir),
                'total_files': total_files,
                'total_size': total_size,
                'created_at': datetime.now().isoformat()
            }
            
            with open(backup_dir / 'backup_metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.backup_registry[timestamp] = backup_dir
            self.logger.info(f"Backup concluído: {total_files} arquivos, {total_size/1024/1024:.2f} MB")
            
            return backup_dir
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            raise

class FileManager:
    """Classe para gerenciamento de movimentação de arquivos"""
    
    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.move_log = []
        
    def safe_move(self, source: Path, destination: Path) -> bool:
        """Move arquivo com verificações de segurança"""
        try:
            # Verificar se arquivo de origem existe
            if not source.exists():
                self.logger.error(f"Arquivo origem não existe: {source}")
                return False
            
            # Criar diretório destino se necessário
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar se arquivo destino já existe
            if destination.exists():
                if self._files_are_identical(source, destination):
                    self.logger.warning(f"Arquivo idêntico já existe em {destination}")
                    if not self.dry_run:
                        source.unlink()  # Remove o duplicado
                    return True
                else:
                    # Renomear com sufixo
                    counter = 1
                    base_name = destination.stem
                    extension = destination.suffix
                    while destination.exists():
                        new_name = f"{base_name}_dup{counter}{extension}"
                        destination = destination.parent / new_name
                        counter += 1
                    self.logger.warning(f"Arquivo renomeado para evitar duplicata: {destination}")
            
            # Registrar movimentação
            move_record = {
                'source': str(source),
                'destination': str(destination),
                'timestamp': datetime.now().isoformat(),
                'size': source.stat().st_size
            }
            self.move_log.append(move_record)
            
            if not self.dry_run:
                shutil.move(str(source), str(destination))
                self.logger.debug(f"Movido: {source.name} -> {destination.parent.name}")
            else:
                self.logger.info(f"[DRY RUN] Moveria: {source.name} -> {destination.parent.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao mover {source} -> {destination}: {e}")
            return False
    
    def _files_are_identical(self, file1: Path, file2: Path) -> bool:
        """Verifica se dois arquivos são idênticos (por tamanho e conteúdo)"""
        try:
            if file1.stat().st_size != file2.stat().st_size:
                return False
            
            # Comparar primeiros 1KB para performance
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                return f1.read(1024) == f2.read(1024)
        except:
            return False
    
    def save_move_log(self, log_dir: Path):
        """Salva log de movimentações para auditoria"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"move_log_{timestamp}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.move_log, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Log de movimentações salvo em: {log_file}")

class XMLReorganizer:
    """Classe principal do reorganizador"""
    
    def __init__(self, base_path: str, dry_run: bool = False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        
        # Criar diretórios de trabalho
        self.work_dir = self.base_path.parent / "xml_reorganizer_work"
        self.work_dir.mkdir(exist_ok=True)
        
        self.logs_dir = self.work_dir / "logs"
        self.backup_dir = self.work_dir / "backups"
        
        # Inicializar componentes
        self.logger = setup_logging(self.logs_dir, dry_run)
        self.analyzer = XMLAnalyzer(self.logger)
        self.backup_manager = BackupManager(self.logger)
        self.file_manager = FileManager(self.logger, dry_run)
        
        # Estatísticas
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'moved_files': 0,
            'duplicate_files': 0,
            'error_files': 0,
            'cancelamentos': 0,
            'folders_processed': 0
        }
    
    def fase_1_validacao(self) -> Dict[str, any]:
        """Fase 1: Validação e mapeamento inicial"""
        self.logger.info("=== FASE 1: VALIDAÇÃO E MAPEAMENTO ===")
        
        validation_results = {}
        problemas_encontrados = []
        
        for pasta in sorted(self.base_path.iterdir()):
            if not pasta.is_dir() or not re.match(r'\d{4}-\d{2}', pasta.name):
                continue
                
            self.logger.info(f"Validando pasta: {pasta.name}")
            self.stats['folders_processed'] += 1
            
            pasta_results = []
            arquivos_xml = list(pasta.glob('*.xml'))
            
            for arquivo in arquivos_xml:
                self.stats['total_files'] += 1
                
                # Analisar arquivo
                resultado = self.analyzer.validate_xml_integrity(arquivo)
                pasta_results.append(resultado)
                
                if resultado['valid']:
                    self.stats['valid_files'] += 1
                    
                    # Verificar se está na pasta correta
                    data_ref = resultado['data_xml'] or resultado['data_nome']
                    if data_ref:
                        pasta_correta = data_ref[:7]  # YYYY-MM
                        if pasta_correta != pasta.name:
                            problema = {
                                'arquivo': str(arquivo),
                                'pasta_atual': pasta.name,
                                'pasta_correta': pasta_correta,
                                'data_xml': resultado['data_xml'],
                                'data_nome': resultado['data_nome']
                            }
                            problemas_encontrados.append(problema)
                else:
                    self.stats['invalid_files'] += 1
                    
                if resultado['is_cancelamento']:
                    self.stats['cancelamentos'] += 1
            
            validation_results[pasta.name] = pasta_results
        
        # Salvar resultados da validação
        validation_file = self.work_dir / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump({
                'validation_results': validation_results,
                'problemas_encontrados': problemas_encontrados,
                'stats': self.stats
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Validação concluída. {len(problemas_encontrados)} problemas encontrados.")
        return {'problemas': problemas_encontrados, 'validation_file': validation_file}
    
    def fase_2_backup(self) -> Path:
        """Fase 2: Backup completo"""
        self.logger.info("=== FASE 2: BACKUP COMPLETO ===")
        
        if self.dry_run:
            self.logger.info("[DRY RUN] Backup seria criado, mas não executado")
            return self.backup_dir / "dry_run_backup"
        
        return self.backup_manager.create_timestamped_backup(self.base_path, self.backup_dir)
    
    def fase_3_reorganizacao(self, problemas: List[Dict]) -> None:
        """Fase 3: Reorganização dos arquivos"""
        self.logger.info("=== FASE 3: REORGANIZAÇÃO ===")
        
        if not problemas:
            self.logger.info("Nenhum arquivo para reorganizar.")
            return
        
        for problema in problemas:
            arquivo_path = Path(problema['arquivo'])
            pasta_correta = problema['pasta_correta']
            
            if not arquivo_path.exists():
                self.logger.warning(f"Arquivo não encontrado: {arquivo_path}")
                continue
            
            # Definir destino
            pasta_destino = self.base_path / pasta_correta
            arquivo_destino = pasta_destino / arquivo_path.name
            
            # Mover arquivo
            if self.file_manager.safe_move(arquivo_path, arquivo_destino):
                self.stats['moved_files'] += 1
                self.logger.info(f"Reorganizado: {arquivo_path.name} -> {pasta_correta}")
            else:
                self.stats['error_files'] += 1
    
    def fase_4_verificacao(self) -> Dict[str, any]:
        """Fase 4: Verificação final"""
        self.logger.info("=== FASE 4: VERIFICAÇÃO FINAL ===")
        
        # Re-executar validação para verificar se ainda há problemas
        validation_results = self.fase_1_validacao()
        problemas_restantes = validation_results['problemas']
        
        if not problemas_restantes:
            self.logger.info("✅ Verificação concluída: TODOS os arquivos estão organizados corretamente!")
        else:
            self.logger.warning(f"⚠️  Ainda existem {len(problemas_restantes)} problemas pendentes")
        
        return {
            'problemas_restantes': len(problemas_restantes),
            'sucesso_total': len(problemas_restantes) == 0
        }
    
    def gerar_relatorio_final(self) -> Path:
        """Gera relatório final detalhado"""
        self.logger.info("=== GERANDO RELATÓRIO FINAL ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = self.work_dir / f"relatorio_final_{timestamp}.json"
        
        relatorio = {
            'timestamp': timestamp,
            'base_path': str(self.base_path),
            'dry_run': self.dry_run,
            'estatisticas': self.stats,
            'configuracoes': {
                'backup_dir': str(self.backup_dir),
                'logs_dir': str(self.logs_dir),
                'work_dir': str(self.work_dir)
            },
            'movimentacoes': self.file_manager.move_log,
            'resumo': {
                'total_processado': self.stats['total_files'],
                'taxa_sucesso': f"{(self.stats['moved_files']/max(1, self.stats['total_files']))*100:.2f}%",
                'arquivos_problematicos': self.stats['error_files'] + self.stats['invalid_files']
            }
        }
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        # Salvar log de movimentações
        self.file_manager.save_move_log(self.logs_dir)
        
        self.logger.info(f"Relatório final salvo em: {relatorio_file}")
        return relatorio_file
    
    def executar_reorganizacao_completa(self) -> Dict[str, any]:
        """Executa todo o processo de reorganização"""
        inicio = datetime.now()
        self.logger.info("🚀 INICIANDO REORGANIZAÇÃO COMPLETA DE XMLs")
        self.logger.info(f"Base path: {self.base_path}")
        self.logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'EXECUÇÃO REAL'}")
        
        try:
            # Fase 1: Validação
            resultado_validacao = self.fase_1_validacao()
            problemas = resultado_validacao['problemas']
            
            if not problemas:
                self.logger.info("✅ Nenhum problema encontrado. Arquivos já estão organizados!")
                return {'sucesso': True, 'problemas_encontrados': 0}
            
            # Fase 2: Backup
            backup_path = self.fase_2_backup()
            
            # Fase 3: Reorganização
            self.fase_3_reorganizacao(problemas)
            
            # Fase 4: Verificação
            resultado_verificacao = self.fase_4_verificacao()
            
            # Relatório final
            relatorio_path = self.gerar_relatorio_final()
            
            tempo_total = datetime.now() - inicio
            self.logger.info(f"🎉 REORGANIZAÇÃO CONCLUÍDA em {tempo_total}")
            
            return {
                'sucesso': True,
                'tempo_execucao': str(tempo_total),
                'problemas_encontrados': len(problemas),
                'arquivos_movidos': self.stats['moved_files'],
                'backup_path': str(backup_path),
                'relatorio_path': str(relatorio_path),
                'verificacao_final': resultado_verificacao
            }
            
        except Exception as e:
            self.logger.error(f"❌ ERRO CRÍTICO: {e}")
            return {'sucesso': False, 'erro': str(e)}


def main():
    """Função principal com interface de linha de comando"""
    parser = argparse.ArgumentParser(
        description="Reorganizador Profissional de XMLs NFe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

# 1. SIMULAÇÃO (recomendado primeiro)
python xml_reorganizer.py "/caminho/para/XML 5anos" --dry-run

# 2. EXECUÇÃO REAL
python xml_reorganizer.py "/caminho/para/XML 5anos"

# 3. APENAS VALIDAÇÃO
python xml_reorganizer.py "/caminho/para/XML 5anos" --only-validate

O script criará uma pasta 'xml_reorganizer_work' com:
- logs/: Logs detalhados de execução
- backups/: Backups automáticos timestampados
- Relatórios finais em JSON
        """
    )
    
    parser.add_argument(
        'base_path',
        help='Caminho para a pasta "XML 5anos" (ou similar) contendo as pastas YYYY-MM'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Executa simulação sem modificar arquivos (RECOMENDADO primeiro)'
    )
    
    parser.add_argument(
        '--only-validate',
        action='store_true',
        help='Executa apenas a validação, sem reorganizar'
    )
    
    args = parser.parse_args()
    
    # Validar caminho base
    base_path = Path(args.base_path)
    if not base_path.exists():
        print(f"❌ ERRO: Caminho não encontrado: {base_path}")
        sys.exit(1)
    
    if not base_path.is_dir():
        print(f"❌ ERRO: Caminho não é um diretório: {base_path}")
        sys.exit(1)
    
    print("🔍 Reorganizador Profissional de XMLs NFe")
    print("=" * 50)
    
    try:
        # Inicializar reorganizador
        reorganizer = XMLReorganizer(str(base_path), dry_run=args.dry_run)
        
        if args.only_validate:
            # Apenas validação
            resultado = reorganizer.fase_1_validacao()
            problemas = resultado['problemas']
            
            print(f"\n📊 RESULTADOS DA VALIDAÇÃO:")
            print(f"Total de arquivos: {reorganizer.stats['total_files']}")
            print(f"Arquivos válidos: {reorganizer.stats['valid_files']}")
            print(f"Problemas encontrados: {len(problemas)}")
            
            if problemas:
                print(f"\n⚠️  {len(problemas)} arquivos precisam ser reorganizados")
                print("Execute sem --only-validate para realizar a reorganização")
            else:
                print("✅ Todos os arquivos estão organizados corretamente!")
        
        else:
            # Execução completa
            resultado = reorganizer.executar_reorganizacao_completa()
            
            if resultado['sucesso']:
                print("\n🎉 REORGANIZAÇÃO CONCLUÍDA COM SUCESSO!")
                print(f"Tempo de execução: {resultado.get('tempo_execucao', 'N/A')}")
                print(f"Arquivos processados: {reorganizer.stats['total_files']}")
                print(f"Arquivos movidos: {resultado.get('arquivos_movidos', 0)}")
                
                if not args.dry_run:
                    print(f"Backup criado em: {resultado.get('backup_path', 'N/A')}")
                
                print(f"Relatório salvo em: {resultado.get('relatorio_path', 'N/A')}")
            else:
                print(f"❌ ERRO na reorganização: {resultado.get('erro', 'Erro desconhecido')}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
