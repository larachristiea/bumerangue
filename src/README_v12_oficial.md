# TaxEngine V12 - Implementação Oficial

Este documento descreve a implementação oficial do TaxEngine V12, que calcula créditos tributários de PIS e COFINS para empresas do Simples Nacional com produtos monofásicos, seguindo estritamente o documento "Mecanismo de funcionamento.v2.json".

## Estrutura do Sistema

- **v12_oficial.py**: Implementação principal do sistema
- **testar_oficial.py**: Script para testar a implementação

## Metodologia de Cálculo

A implementação segue rigorosamente os passos descritos no documento de referência:

1. **Extração e elaboração de dados a partir do PGDAS**:
   - Período de apuração
   - Receita bruta mensal
   - Receita bruta dos 12 meses anteriores
   - Alíquota efetiva
   - Percentuais de tributos

2. **Utilização dos dados extraídos do XML**:
   - Cálculo da receita bruta de vendas (RBV)
   - Cálculo da receita sem descontos (RSD)
   - Classificação de produtos monofásicos x não monofásicos
     - **IMPORTANTE**: A classificação utiliza EXCLUSIVAMENTE a tabela de NCMs monofásicas

3. **Cálculo de tributos devidos**:
   - Para produtos monofásicos: PIS e COFINS são ZERO
   - Para produtos não monofásicos: todos os tributos são calculados normalmente

4. **Cálculo do crédito tributário**:
   - PIS declarado - PIS apurado
   - COFINS declarado - COFINS apurado
   - Atualização pela taxa SELIC

## Resultados - Dezembro 2024

Os resultados do processamento para dezembro de 2024 são:

- **Receita Bruta PGDAS**: R$ 108.479,77
- **Receita Bruta Vendas (XML)**: R$ 107.463,41
- **Receita Monofásicos**: R$ 79.390,20 (73,88%)
- **Receita Não-Monofásicos**: R$ 28.073,21 (26,12%)
- **PIS declarado**: R$ 100,70
- **COFINS declarado**: R$ 464,81
- **PIS apurado**: R$ 45,17
- **COFINS apurado**: R$ 208,51
- **Crédito PIS**: R$ 55,53
- **Crédito COFINS**: R$ 256,30
- **Crédito Total**: R$ 311,83
- **Crédito Atualizado (SELIC 1,0408)**: R$ 324,55

## Diferenças da Implementação Anterior

A implementação oficial difere da anterior principalmente nos seguintes aspectos:

1. **Classificação de Produtos**: Utiliza EXCLUSIVAMENTE a tabela de NCMs monofásicas, sem considerar códigos CST
2. **Valor Zero para PIS/COFINS**: Explicita que produtos monofásicos devem ter PIS e COFINS zerados no cálculo
3. **Estrutura de Cálculo**: Segue estritamente a metodologia do documento de referência

## Uso do Sistema

Para executar a análise de um período:

```bash
python3 src/testar_oficial.py
```

Os resultados são salvos em `/data/resultados/resultado_oficial_[periodo].json` e exibidos no console.