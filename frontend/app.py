#!/usr/bin/env python3
"""
Frontend Web para Motor de Notas - Sistema de Processamento de NFe e PGDAS
Desenvolvido para MacBook Pro M1 8GB

Funcionalidades:
- Upload de pasta ZIP com XMLs de NFe
- Upload de arquivo PGDAS (PDF)
- Processamento automático dos dados
- Dashboard com resultados e análises
- Visualizações interativas
"""

import os
import json
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import shutil

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

# Importar módulos do sistema existente
import sys
sys.path.append('/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2/application')
from parser import processar_xmls, calcular_creditos

app = Flask(__name__)
app.secret_key = 'motor_notas_secret_key_2025'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB máximo

# Configurações de diretórios
BASE_DIR = Path('/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2')
UPLOAD_FOLDER = BASE_DIR / 'frontend' / 'uploads'
RESULTS_FOLDER = BASE_DIR / 'frontend' / 'results'
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'json'}

# Criar diretórios necessários
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

def allowed_file(filename, extensions=None):
    if extensions is None:
        extensions = ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def extract_zip_files(zip_path, extract_to):
    """Extrai arquivos ZIP e organiza XMLs"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Encontrar todos os XMLs recursivamente
        xml_files = []
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
        
        return xml_files
    except Exception as e:
        raise Exception(f"Erro ao extrair ZIP: {str(e)}")

def processar_pgdas_pdf(pdf_path):
    """Processa arquivo PDF do PGDAS e extrai dados estruturados"""
    # Por enquanto, retorna dados simulados
    # TODO: Implementar extração real do PDF do PGDAS
    return {
        "dados_estruturados": {
            "aliquota_apurada": 0.0576  # 5.76%
        },
        "proporcoes": {
            "pis": 0.0276,      # 27.6%
            "cofins": 0.1274    # 127.4%
        },
        "tributos": {
            "pis": 15000.00,
            "cofins": 69000.00
        }
    }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Endpoint para upload dos arquivos"""
    try:
        # Verificar se os arquivos foram enviados
        if 'xml_zip' not in request.files or 'pgdas_pdf' not in request.files:
            flash('Arquivos XML ZIP e PGDAS PDF são obrigatórios')
            return redirect(url_for('index'))
        
        xml_zip = request.files['xml_zip']
        pgdas_pdf = request.files['pgdas_pdf']
        periodo = request.form.get('periodo', datetime.now().strftime('%Y-%m'))
        
        if xml_zip.filename == '' or pgdas_pdf.filename == '':
            flash('Selecione ambos os arquivos')
            return redirect(url_for('index'))
        
        if not (allowed_file(xml_zip.filename, {'zip'}) and allowed_file(pgdas_pdf.filename, {'pdf'})):
            flash('Tipos de arquivo inválidos. Use ZIP para XMLs e PDF para PGDAS')
            return redirect(url_for('index'))
        
        # Criar diretório para este processamento
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_dir = UPLOAD_FOLDER / f'session_{timestamp}'
        session_dir.mkdir(exist_ok=True)
        
        # Salvar arquivos
        xml_zip_path = session_dir / secure_filename(xml_zip.filename)
        pgdas_pdf_path = session_dir / secure_filename(pgdas_pdf.filename)
        
        xml_zip.save(xml_zip_path)
        pgdas_pdf.save(pgdas_pdf_path)
        
        # Extrair XMLs
        xml_extract_dir = session_dir / 'xmls'
        xml_extract_dir.mkdir(exist_ok=True)
        xml_files = extract_zip_files(xml_zip_path, xml_extract_dir)
        
        if not xml_files:
            flash('Nenhum arquivo XML encontrado no ZIP')
            return redirect(url_for('index'))
        
        # Processar arquivos
        flash(f'Processando {len(xml_files)} XMLs e PGDAS...')
        
        # Processar XMLs
        notas = processar_xmls(str(xml_extract_dir))
        
        if not notas:
            flash('Nenhuma nota fiscal válida encontrada')
            return redirect(url_for('index'))
        
        # Processar PGDAS (simulado por enquanto)
        dados_pgdas = processar_pgdas_pdf(pgdas_pdf_path)
        
        # Calcular créditos
        resultados = calcular_creditos(notas, dados_pgdas)
        
        # Salvar resultados
        resultado_path = RESULTS_FOLDER / f'resultado_{timestamp}.json'
        with open(resultado_path, 'w', encoding='utf-8') as f:
            json.dump({
                'periodo': periodo,
                'timestamp': timestamp,
                'arquivos': {
                    'xml_zip': xml_zip.filename,
                    'pgdas_pdf': pgdas_pdf.filename,
                    'qtd_xmls': len(xml_files)
                },
                'resultados': resultados
            }, f, indent=2, ensure_ascii=False)
        
        return redirect(url_for('dashboard', session_id=timestamp))
        
    except Exception as e:
        flash(f'Erro no processamento: {str(e)}')
        return redirect(url_for('index'))

@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Dashboard com resultados do processamento"""
    try:
        resultado_path = RESULTS_FOLDER / f'resultado_{session_id}.json'
        
        if not resultado_path.exists():
            flash('Sessão não encontrada')
            return redirect(url_for('index'))
        
        with open(resultado_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        resultados = dados['resultados']
        
        return render_template('dashboard.html', 
                             dados=dados, 
                             resultados=resultados)
        
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/resultados/<session_id>')
def api_resultados(session_id):
    """API endpoint para dados do dashboard"""
    try:
        resultado_path = RESULTS_FOLDER / f'resultado_{session_id}.json'
        
        if not resultado_path.exists():
            return jsonify({'error': 'Sessão não encontrada'}), 404
        
        with open(resultado_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        return jsonify(dados)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historico')
def historico():
    """Página com histórico de processamentos"""
    try:
        resultados = []
        
        for arquivo in RESULTS_FOLDER.glob('resultado_*.json'):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                resultados.append({
                    'session_id': dados['timestamp'],
                    'periodo': dados.get('periodo', 'N/A'),
                    'data_processamento': datetime.strptime(dados['timestamp'], '%Y%m%d_%H%M%S'),
                    'qtd_xmls': dados['arquivos']['qtd_xmls'],
                    'credito_total': dados['resultados']['creditos']['total']
                })
            except Exception:
                continue
        
        # Ordenar por data (mais recente primeiro)
        resultados.sort(key=lambda x: x['data_processamento'], reverse=True)
        
        return render_template('historico.html', resultados=resultados)
        
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}')
        return redirect(url_for('index'))

# Filtro personalizado para o Jinja2
@app.template_filter('tojsonfilter')
def to_json_filter(obj):
    return json.dumps(obj)

if __name__ == '__main__':
    print("🚀 Iniciando Motor de Notas Frontend")
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"📤 Upload Folder: {UPLOAD_FOLDER}")
    print(f"📊 Results Folder: {RESULTS_FOLDER}")
    print("🌐 Acesse: http://localhost:5000")
    
    # Desenvolvimento - usar debug=True
    app.run(host='0.0.0.0', port=5000, debug=True)