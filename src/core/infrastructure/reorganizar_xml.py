#!/usr/bin/env python3
"""
Script de Reorganização de XMLs NFe
Organiza arquivos por data real de emissão
"""

import os
import re
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from datetime import datetime
import argparse

def extrair_data_do_xml(arquivo_path):
    """Extrai data de emissão do XML"""
    try:
        tree = ET.parse(arquivo_path)
        root = tree.getroot()
        
        # Buscar dhEmi com e sem namespace
        for elem in root.iter():
            if elem.tag.endswith('dhEmi'):
                data_completa = elem.text
                if data_completa:
                    return data_completa.split('T')[0]  # YYYY-MM-DD
    except Exception as e:
        print(f"Erro ao ler {arquivo_path}: {e}")
    return None

def extrair_data_do_nome(nome_arquivo):
    """Extrai data do nome do arquivo NFe: UF+AAMM+DD"""
    if len(nome_arquivo) >= 8:
        ano_mes = nome_arquivo[2:6]  # posições 2-5
        dia = nome_arquivo[6:8]      # posições 6-7
        
        ano = '20' + ano_mes[:2]     # 20 + AA
        mes = ano_mes[2:4]           # MM
        
        try:
            if 1 <= int(mes) <= 12:
                return f"{ano}-{mes}-{dia}"
        except:
            pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Reorganiza XMLs por data de emissão")
    parser.add_argument('--xml-dir', required=True, help='Caminho da pasta de XMLs')
    args = parser.parse_args()

    base_path = args.xml_dir
    
    print("=== REORGANIZAÇÃO DE XMLs INICIADA ===")
    print(f"Pasta base: {base_path}")
    print(f"Backup em: BACKUP_XML_REORGANIZACAO/")
    print()
    
    arquivos_movidos = 0
    arquivos_analisados = 0
    erros = 0
    
    # Analisar todas as pastas
    for pasta in sorted(os.listdir(base_path)):
        pasta_path = os.path.join(base_path, pasta)
        
        if not os.path.isdir(pasta_path) or not re.match(r'\d{4}-\d{2}', pasta):
            continue
            
        print(f"Processando pasta: {pasta}")
        
        # Analisar arquivos da pasta
        arquivos_xml = [f for f in os.listdir(pasta_path) if f.endswith('.xml')]
        
        for arquivo in arquivos_xml:
            arquivos_analisados += 1
            arquivo_path = os.path.join(pasta_path, arquivo)
            
            try:
                # Extrair data (priorizar XML, usar nome como backup)
                data_xml = extrair_data_do_xml(arquivo_path)
                data_nome = extrair_data_do_nome(arquivo)
                
                data_referencia = data_xml if data_xml else data_nome
                
                if data_referencia:
                    pasta_correta = data_referencia[:7]  # YYYY-MM
                    
                    # Verificar se está na pasta errada
                    if pasta_correta != pasta:
                        pasta_destino = os.path.join(base_path, pasta_correta)
                        
                        # Criar pasta destino se não existir
                        os.makedirs(pasta_destino, exist_ok=True)
                        
                        # Mover arquivo
                        arquivo_destino = os.path.join(pasta_destino, arquivo)
                        
                        # Se arquivo já existe no destino, pular
                        if os.path.exists(arquivo_destino):
                            print(f"  Já existe: {arquivo} -> {pasta_correta}")
                        else:
                            shutil.move(arquivo_path, arquivo_destino)
                            print(f"  Movido: {arquivo} -> {pasta_correta}")
                            arquivos_movidos += 1
                
            except Exception as e:
                print(f"  Erro em {arquivo}: {e}")
                erros += 1
    
    print()
    print("=== REORGANIZAÇÃO CONCLUÍDA ===")
    print(f"Arquivos analisados: {arquivos_analisados}")
    print(f"Arquivos movidos: {arquivos_movidos}")
    print(f"Erros: {erros}")
    print()
    print("✅ Reorganização concluída com sucesso!")

if __name__ == "__main__":
    main()
