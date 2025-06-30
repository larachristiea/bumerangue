#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_date_from_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for elem in root.iter():
            if 'dhEmi' in elem.tag:
                if elem.text:
                    date_str = elem.text.split('T')[0]
                    year_month = '-'.join(date_str.split('-')[:2])
                    return year_month
        return None
    except:
        return None

def main():
    source_dir = "/Users/mcplara/Desktop/MAIS ATUALIZADO V12- ZERADO RESETADO ASPIRADO OPTIMUSPRIME MEGAZORD LIMPO/data/XML 5anos"
    
    if not os.path.exists(source_dir):
        print(f"❌ Pasta não encontrada: {source_dir}")
        return
    
    print(f"📁 Analisando pasta: {source_dir}")
    print("=" * 60)
    
    source_path = Path(source_dir)
    xml_files_root = list(source_path.glob("*.xml"))
    print(f"📄 Arquivos XML na pasta principal: {len(xml_files_root)}")
    
    date_folders = [d for d in source_path.iterdir() if d.is_dir() and d.name != '.DS_Store']
    print(f"📂 Pastas de organização existentes: {len(date_folders)}")
    
    if date_folders:
        print("\n📅 Estrutura atual:")
        for folder in sorted(date_folders):
            xml_count = len(list(folder.glob("*.xml")))
            print(f"   📁 {folder.name}: {xml_count} arquivo(s)")
    
    if xml_files_root:
        print("\n🔍 Analisando arquivos XML soltos (primeiros 5)...")
        for xml_file in xml_files_root[:5]:
            emission_date = extract_date_from_xml(xml_file)
            print(f"📄 {xml_file.name[:40]} -> {emission_date or 'SEM DATA'}")
    else:
        print("\n✅ Não há arquivos XML soltos - todos já organizados!")
        if date_folders:
            sample_folder = date_folders[0]
            sample_xmls = list(sample_folder.glob("*.xml"))
            if sample_xmls:
                sample_xml = sample_xmls[0]
                emission_date = extract_date_from_xml(sample_xml)
                print(f"🔍 Teste: {sample_xml.name} -> {emission_date}")

if __name__ == "__main__":
    main()
