# 🌐 Frontend Web - Motor de Notas

Interface web moderna para o sistema de processamento de NFe e cálculo de créditos tributários PIS/COFINS.

## 🚀 Configuração Rápida (MacBook Pro M1)

### Opção 1: Script Automático
```bash
cd /Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO\ 2/frontend
./start.sh
```

### Opção 2: Configuração Manual
```bash
# 1. Navegar para o diretório
cd /Users/mcplara/Desktop/MOTOR_NOTAS_LIMPO\ 2

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt
pip install -r frontend/frontend_requirements.txt

# 4. Iniciar servidor
cd frontend
python app.py
```

## 🌟 Funcionalidades

### 📤 Upload de Arquivos
- **Upload de ZIP com XMLs**: Arraste e solte ou clique para selecionar
- **Upload de PGDAS PDF**: Documento fiscal do período correspondente
- **Validação automática**: Verifica tipos de arquivo e tamanhos
- **Processamento em tempo real**: Feedback visual do progresso

### 📊 Dashboard Interativo
- **Métricas principais**: Créditos totais, proporções, alíquotas
- **Gráficos dinâmicos**: Pizza e barras com Chart.js
- **Tabelas detalhadas**: Resumo completo dos cálculos
- **Exportação de dados**: JSON para análises posteriores

### 📈 Visualizações
- **Distribuição por tipo**: Monofásico vs Não-monofásico
- **Comparativo tributário**: Recolhido vs Devido
- **Estatísticas detalhadas**: Por categoria e período
- **Animações**: Números animados e transições suaves

### 📋 Histórico
- **Lista de processamentos**: Todos os cálculos anteriores
- **Busca por período**: Filtros por data e valores
- **Acesso rápido**: Visualizar qualquer resultado anterior

## 🔧 Estrutura do Frontend

```
frontend/
├── app.py                 # Aplicação Flask principal
├── start.sh              # Script de inicialização
├── frontend_requirements.txt # Dependências específicas
├── templates/            # Templates HTML
│   ├── base.html        # Template base
│   ├── index.html       # Página inicial
│   ├── dashboard.html   # Dashboard de resultados
│   └── historico.html   # Histórico de processamentos
├── uploads/             # Arquivos enviados (auto-criado)
└── results/             # Resultados processados (auto-criado)
```

## 🎯 Como Usar

### 1. Preparar Arquivos
- **ZIP de XMLs**: Todos os XMLs de NFe do período em um arquivo ZIP
- **PGDAS PDF**: Documento do mesmo período dos XMLs
- **Período**: Selecionar mês/ano de referência

### 2. Fazer Upload
1. Acesse http://localhost:5000
2. Selecione o período de referência
3. Arraste o ZIP com XMLs ou clique para selecionar
4. Arraste o PDF do PGDAS ou clique para selecionar
5. Clique em "Processar Arquivos"

### 3. Visualizar Resultados
- Dashboard será exibido automaticamente
- Métricas principais no topo
- Gráficos interativos
- Tabelas detalhadas
- Opções de exportação

### 4. Acessar Histórico
- Menu "Histórico" para ver processamentos anteriores
- Clique em "Visualizar" para reabrir qualquer resultado

## 📱 Interface Responsiva

### Desktop (MacBook Pro)
- Layout otimizado para telas grandes
- Gráficos em colunas lado a lado
- Tabelas com scroll horizontal quando necessário

### Mobile/Tablet
- Cards empilhados verticalmente
- Botões e textos otimizados para toque
- Gráficos redimensionados automaticamente

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 2.3+**: Framework web Python
- **Werkzeug**: Utilities para upload de arquivos
- **Sistema existente**: Integração com parser.py e main.py

### Frontend
- **Bootstrap 5.3**: Framework CSS responsivo
- **Chart.js 3.9**: Gráficos interativos
- **Font Awesome 6.4**: Ícones modernos
- **JavaScript ES6+**: Funcionalidades avançadas

### Recursos Especiais
- **Drag & Drop**: Upload intuitivo de arquivos
- **Animações CSS**: Transições suaves
- **Formatação brasileira**: Moeda e percentuais em pt-BR
- **Feedback visual**: Loading e validações em tempo real

## ⚙️ Configurações Avançadas

### Limites de Upload
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### Diretórios Personalizados
```python
UPLOAD_FOLDER = BASE_DIR / 'frontend' / 'uploads'
RESULTS_FOLDER = BASE_DIR / 'frontend' / 'results'
```

### Debug Mode
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🔍 Troubleshooting

### Erro: "Módulo não encontrado"
```bash
# Verificar se o ambiente virtual está ativo
source venv/bin/activate

# Reinstalar dependências
pip install -r frontend/frontend_requirements.txt
```

### Erro: "Porta 5000 em uso"
```bash
# Verificar processos na porta 5000
lsof -i :5000

# Matar processo se necessário
kill -9 <PID>
```

### Arquivos não são processados
- Verificar se o ZIP contém XMLs válidos
- Certificar-se de que o PDF é do PGDAS
- Verificar permissões de diretório

### Performance no M1
- Sistema otimizado para ARM64
- Use Python 3.8+ nativo para M1
- Ambiente virtual isolado evita conflitos

## 📊 Exemplo de Uso

1. **Período**: 2024-03
2. **XMLs**: `notas_marco_2024.zip` (150 XMLs)
3. **PGDAS**: `pgdas_03_2024.pdf`
4. **Resultado**: Dashboard com R$ 45.230,15 de créditos

## 🚀 Próximas Funcionalidades

- [ ] Extração automática de dados do PDF do PGDAS
- [ ] Gráficos de tendência histórica
- [ ] Exportação para Excel
- [ ] API REST para integração
- [ ] Notificações por email
- [ ] Backup automático na nuvem

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar este README
2. Consultar logs do sistema
3. Testar com dados de exemplo
4. Documentação técnica em `docs/`

---

**Versão**: 2025.1  
**Compatibilidade**: macOS (M1), Python 3.8+  
**Status**: ✅ Estável e Funcional