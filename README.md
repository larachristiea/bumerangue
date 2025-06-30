# 🚀 MOTOR NOTAS ORGANIZADAS - SISTEMA LIMPO

Sistema genérico para processamento, análise e organização de documentos fiscais eletrônicos (NF-e, PGDAS, XML, JSON, XLSX) para qualquer cliente ou cenário contábil/fiscal.

## 📁 ESTRUTURA LIMPA E ORGANIZADA

```
MOTOR_NOTAS_LIMPO/
├── src/                    # Código fonte principal
│   ├── core/              # Lógica de negócio
│   └── interface/         # Interfaces e CLI
├── application/           # Scripts de processamento
├── tests/                 # Testes automatizados
├── docs/                  # Documentação consolidada
├── deprecated/            # Arquivos antigos/experimentais
├── requirements.txt       # Dependências Python
├── setup.py              # Configuração do projeto
└── README.md             # Esta documentação
```

## 🛠️ INSTALAÇÃO E CONFIGURAÇÃO

### Pré-requisitos
- Python 3.8+
- pip package manager

### Configuração do Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual FORA do projeto
cd ~/
python -m venv venv_motor_notas
source venv_motor_notas/bin/activate  # macOS/Linux

# Instalar dependências
cd /caminho/para/MOTOR_NOTAS_LIMPO
pip install -r requirements.txt
```

## 🚀 COMO USAR

### 1. Processamento Básico de NFe
```python
from application.main import processar_nfe
resultado = processar_nfe(arquivo_xml="caminho/para/nfe.xml")
```

### 2. Análise de PGDAS
```python
from application.extrair_pgdas import extrair_dados_pgdas
dados = extrair_dados_pgdas(arquivo_pdf="caminho/para/pgdas.pdf")
```

### 3. Cálculo de Créditos
```python
from application.calculo_credito_generico import calcular_credito_generico
resultado = calcular_credito_generico(
    rbt12=1000000,
    receita_nao_mono=500000,
    pis_declarado=1000,
    cofins_declarado=4000
)
```

## 📊 FUNCIONALIDADES PRINCIPAIS

- ✅ **Parser NFe Híbrido** - Processamento robusto de XML
- ✅ **Extrator PGDAS** - Análise de PDFs fiscais  
- ✅ **Validadores Fiscais** - CNPJ, CPF, NCM, etc.
- ✅ **Cálculo de Créditos** - PIS/COFINS automático
- ✅ **Processamento Batch** - Múltiplos arquivos
- ✅ **Logs Estruturados** - Rastreabilidade completa

## 🧪 TESTES

```bash
# Executar todos os testes
python -m pytest tests/

# Teste específico
python -m pytest tests/test_parser.py -v
```

## 📋 BOAS PRÁTICAS

1. **Sempre use ambiente virtual** - Evita conflitos de dependências
2. **Não armazene dados sensíveis** - Use arquivos de configuração
3. **Documente alterações** - Mantenha logs de modificações
4. **Teste antes de deploy** - Execute testes unitários

## 🔧 DESENVOLVIMENTO

### Adicionar Nova Funcionalidade
1. Criar branch: `git checkout -b feature/nova-funcionalidade`
2. Implementar em `src/` ou `application/`
3. Adicionar testes em `tests/`
4. Documentar em `docs/`
5. Fazer commit e PR

### Estrutura de Commit
```
feat: adiciona novo extrator para XMLs
fix: corrige validação de CNPJ
docs: atualiza documentação da API
test: adiciona testes para parser
```

## 📖 DOCUMENTAÇÃO ADICIONAL

- [Documentação Técnica](docs/DOCUMENTACAO_TECNICA.md)
- [Guia de Contribuição](docs/CONTRIBUTING.md)
- [Changelog](docs/CHANGELOG.md)

---

**Versão Limpa**: 2025.1  
**Última Atualização**: Junho 2025  
**Status**: 🟢 Estável e Funcional
