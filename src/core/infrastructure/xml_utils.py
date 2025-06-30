#!/usr/bin/env python3
"""
Utilitários auxiliares para o reorganizador de XMLs
- Rollback de operações
- Verificação de integridade
- Limpeza de arquivos de trabalho
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import argparse

def list_backups(work_dir: Path) -> list:
    """Lista todos os backups disponíveis"""
    backup_dir = work_dir / "backups"
    if not backup_dir.exists():
        return []
    
    backups = []
    for item in backup_dir.iterdir():
        if item.is_dir() and item.name.startswith("backup_"):
            metadata_file = item / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                backups.append({
                    'path': item,
                    'timestamp': metadata.get('timestamp', 'unknown'),
                    'total_files': metadata.get('total_files', 0),
                    'created_at': metadata.get('created_at', 'unknown')
                })
    
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

def restore_backup(backup_path: Path, target_path: Path, dry_run: bool = False) -> bool:
    """Restaura um backup específico"""
    print(f"{'[DRY RUN] ' if dry_run else ''}Restaurando backup:")
    print(f"  De: {backup_path}")
    print(f"  Para: {target_path}")
    
    if not backup_path.exists():
        print(f"❌ Backup não encontrado: {backup_path}")
        return False
    
    # Verificar se já existe conteúdo no destino
    if target_path.exists() and any(target_path.iterdir()):
        response = input("⚠️  O diretório de destino não está vazio. Sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("Operação cancelada.")
            return False
    
    if not dry_run:
        try:
            # Limpar destino se existir
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # Copiar backup
            shutil.copytree(backup_path, target_path)
            print("✅ Backup restaurado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False
    else:
        print("✅ [DRY RUN] Backup seria restaurado com sucesso!")
        return True

def verify_structure(base_path: Path) -> dict:
    """Verifica estrutura e integridade dos arquivos"""
    print("🔍 Verificando estrutura...")
    
    stats = {
        'total_folders': 0,
        'total_files': 0,
        'valid_xml': 0,
        'invalid_xml': 0,
        'missing_folders': [],
        'extra_files': []
    }
    
    # Verificar pastas esperadas (últimos 36 meses)
    from datetime import datetime, timedelta
    current = datetime.now()
    expected_folders = []
    
    for i in range(36):
        date = current - timedelta(days=30 * i)
        folder_name = date.strftime("%Y-%m")
        expected_folders.append(folder_name)
    
    # Verificar pastas existentes
    for item in base_path.iterdir():
        if item.is_dir():
            stats['total_folders'] += 1
            
            # Contar arquivos XML
            xml_files = list(item.glob("*.xml"))
            stats['total_files'] += len(xml_files)
            
            # Verificação básica de XML
            for xml_file in xml_files[:10]:  # Verificar apenas 10 por pasta para performance
                try:
                    import xml.etree.ElementTree as ET
                    ET.parse(xml_file)
                    stats['valid_xml'] += 1
                except:
                    stats['invalid_xml'] += 1
        else:
            stats['extra_files'].append(item.name)
    
    # Verificar pastas faltantes
    existing_folders = [item.name for item in base_path.iterdir() if item.is_dir()]
    for expected in expected_folders[:12]:  # Últimos 12 meses
        if expected not in existing_folders:
            stats['missing_folders'].append(expected)
    
    return stats

def cleanup_work_directory(work_dir: Path, keep_days: int = 30, dry_run: bool = False) -> None:
    """Limpa arquivos antigos do diretório de trabalho"""
    print(f"🧹 {'[DRY RUN] ' if dry_run else ''}Limpando arquivos antigos (>{keep_days} dias)...")
    
    cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)
    removed_count = 0
    
    for root, dirs, files in os.walk(work_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.stat().st_mtime < cutoff_date:
                print(f"  Removendo: {file_path}")
                if not dry_run:
                    file_path.unlink()
                removed_count += 1
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Removidos {removed_count} arquivos antigos.")

def main():
    parser = argparse.ArgumentParser(description="Utilitários para reorganizador XML")
    parser.add_argument('work_dir', help='Diretório de trabalho do reorganizador')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: list-backups
    list_parser = subparsers.add_parser('list-backups', help='Lista backups disponíveis')
    
    # Comando: restore
    restore_parser = subparsers.add_parser('restore', help='Restaura um backup')
    restore_parser.add_argument('backup_timestamp', help='Timestamp do backup (ex: 20250526_150030)')
    restore_parser.add_argument('target_path', help='Caminho onde restaurar')
    restore_parser.add_argument('--dry-run', action='store_true', help='Simular restauração')
    
    # Comando: verify
    verify_parser = subparsers.add_parser('verify', help='Verifica estrutura de diretórios')
    verify_parser.add_argument('base_path', help='Caminho base para verificar')
    
    # Comando: cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpa arquivos antigos')
    cleanup_parser.add_argument('--keep-days', type=int, default=30, help='Dias para manter arquivos')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Simular limpeza')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    work_dir = Path(args.work_dir)
    
    if args.command == 'list-backups':
        backups = list_backups(work_dir)
        if not backups:
            print("Nenhum backup encontrado.")
        else:
            print(f"📦 {len(backups)} backup(s) encontrado(s):")
            for backup in backups:
                print(f"  {backup['timestamp']} - {backup['total_files']} arquivos - {backup['created_at']}")
    
    elif args.command == 'restore':
        backup_path = work_dir / "backups" / f"backup_{args.backup_timestamp}"
        target_path = Path(args.target_path)
        restore_backup(backup_path, target_path, args.dry_run)
    
    elif args.command == 'verify':
        base_path = Path(args.base_path)
        stats = verify_structure(base_path)
        print("\n📊 Estatísticas da estrutura:")
        print(f"  Pastas: {stats['total_folders']}")
        print(f"  Arquivos XML: {stats['total_files']}")
        print(f"  XMLs válidos verificados: {stats['valid_xml']}")
        print(f"  XMLs inválidos: {stats['invalid_xml']}")
        if stats['missing_folders']:
            print(f"  ⚠️  Pastas faltantes: {', '.join(stats['missing_folders'])}")
        if stats['extra_files']:
            print(f"  ⚠️  Arquivos extras: {', '.join(stats['extra_files'])}")
    
    elif args.command == 'cleanup':
        cleanup_work_directory(work_dir, args.keep_days, args.dry_run)

if __name__ == "__main__":
    main()
