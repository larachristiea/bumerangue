#!/usr/bin/env python3
import argparse
import os
import xml.etree.ElementTree as ET
import json

def load_ncms(ncmlist_file):
    ext = os.path.splitext(ncmlist_file)[1].lower()
    codes = set()
    if ext == '.json':
        data = json.load(open(ncmlist_file, 'r', encoding='utf-8'))
        for item in data:
            num = item.get('NCMs monofásicos') or item.get('NCM')
            if num is not None:
                code = str(num).zfill(8)
                codes.add(code)
    else:
        with open(ncmlist_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    codes.add(line.zfill(8))
    return codes

def extract_descriptions(xml_dir, ncms):
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    mapping = {ncm: set() for ncm in ncms}
    for root_dir, _, files in os.walk(xml_dir):
        for fname in files:
            if not fname.lower().endswith('.xml'):
                continue
            path = os.path.join(root_dir, fname)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                for prod in root.findall('.//{http://www.portalfiscal.inf.br/nfe}prod'):
                    ncm_elem = prod.find('nfe:NCM', ns)
                    xprod_elem = prod.find('nfe:xProd', ns)
                    if ncm_elem is None or xprod_elem is None:
                        continue
                    code = ncm_elem.text.strip()
                    if code in ncms:
                        mapping[code].add(xprod_elem.text.strip())
            except Exception:
                continue
    return mapping

def main():
    parser = argparse.ArgumentParser(description="Extrai descrições de produtos por NCM")
    parser.add_argument('--xml-dir', required=True, help='Diretório de XMLs')
    parser.add_argument('--ncmlist', default='data/tabelas/Espelho de ncms monofásicas.json', help='Arquivo JSON com NCMs monofásicos')
    args = parser.parse_args()

    ncms = load_ncms(args.ncmlist)
    mapping = extract_descriptions(args.xml_dir, ncms)
    for ncm, descs in mapping.items():
        print(f"NCM {ncm} ({len(descs)} descrições):")
        for d in sorted(descs):
            print(f"  - {d}")
        print()

if __name__ == "__main__":
    main()
