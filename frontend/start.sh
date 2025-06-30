#!/bin/bash

# Script de Inicialização do Motor de Notas Frontend
# Otimizado para MacBook Pro M1 8GB

echo "🚀 Inicializando Motor de Notas Frontend"
echo "💻 MacBook Pro M1 - Sistema Otimizado"
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2" ]; then
    echo "❌ Erro: Diretório do projeto não encontrado"
    echo "   Certifique-se de que o projeto está em /Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2"
    exit 1
fi

# Navegar para o diretório do projeto
cd "/Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO 2"

echo "📁 Diretório do projeto: $(pwd)"

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3.8+ primeiro."
    exit 1
fi

echo "🐍 Python: $(python3 --version)"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências do sistema principal
echo "📚 Instalando dependências do sistema..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  Arquivo requirements.txt não encontrado"
fi

# Instalar dependências do frontend
echo "🌐 Instalando dependências do frontend..."
if [ -f "frontend/frontend_requirements.txt" ]; then
    pip install -r frontend/frontend_requirements.txt
else
    echo "⚠️  Arquivo frontend_requirements.txt não encontrado"
fi

# Verificar estrutura de diretórios
echo "📂 Verificando estrutura de diretórios..."
mkdir -p frontend/uploads
mkdir -p frontend/results
mkdir -p frontend/static
mkdir -p frontend/templates

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "🌟 Para iniciar o servidor:"
echo "   cd frontend"
echo "   python app.py"
echo ""
echo "🌐 Depois acesse: http://localhost:5000"
echo ""
echo "📋 Comandos úteis:"
echo "   Para parar: Ctrl+C"
echo "   Para desativar o ambiente virtual: deactivate"
echo ""