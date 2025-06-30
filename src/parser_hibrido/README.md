# Parser Híbrido de NFe

Parser robusto que combina validação fiscal completa com funcionalidades avançadas de negócio.

## Características Principais

- Validação Robusta: CNPJ, NCM, CFOP, CST com regras fiscais específicas
- Logging Estruturado: Rastreabilidade completa com níveis INFO/WARNING/ERROR
- Precisão Fiscal: Usa Decimal para valores monetários (zero imprecisão)
- Arquitetura OO: Classes bem estruturadas para NFe e itens
- Integração Completa: Processamento de cancelamentos + PGDAS + cálculos tributários
- Testado: Suite completa de testes automatizados
- Compatível: Integra com sistema existente sem quebrar funcionalidades

## Instalação

```bash
# Testar instalação
python testes.py --rapido

# Instalar dependências se necessário
pip install lxml>=4.6.0 python-dateutil>=2.8.0
```

## Uso Rápido

```python
from parser_hibrido import processar_xml_nfe_hibrido

# Processar um XML
nota_fiscal = processar_xml_nfe_hibrido(xml_content)

if nota_fiscal:
    print(f"NFe: {nota_fiscal.numero}")
    print(f"Emitente: {nota_fiscal.emitente_nome}")
    print(f"Valor: R$ {nota_fiscal.valor_total_nf:.2f}")
```

## Migração do Sistema Existente

```bash
# Migração automática
python migracao_sistema.py --migrar

# Processar período específico
python migracao_sistema.py --periodo 2024-12
```

## Testes

```bash
# Teste rápido
python testes.py --rapido

# Exemplo de uso
python exemplo_uso.py
```

## Comparação: Parser Original vs Híbrido

| Funcionalidade | Original | Híbrido |
|---|---|---|
| Validação CNPJ/CPF | Básica | Robusta |
| Validação NCM/CFOP | Nenhuma | Completa |
| Logging | Prints básicos | Estruturado |
| Precisão Monetária | Float (impreciso) | Decimal (exato) |
| Tratamento de Erros | Básico | Completo |
| Classes OO | Sim | Aprimoradas |
| Testes Automatizados | Não | Completos |

Parser híbrido implementado com sucesso!
