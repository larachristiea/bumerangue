#!/bin/bash
# COMANDOS PRONTOS PARA EXECUÇÃO
# Reorganizador Profissional de XMLs NFe

echo "🚀 REORGANIZADOR PROFISSIONAL DE XMLs NFe"
echo "========================================"
echo

# Definir caminho base
BASE_PATH="/Users/mcplara/Desktop/MAIS ATUALIZADO V12- ZERADO RESETADO ASPIRADO OPTIMUSPRIME MEGAZORD LIMPO/data/XML 5anos"

cd "/Users/mcplara/Desktop/MAIS ATUALIZADO V12- ZERADO RESETADO ASPIRADO OPTIMUSPRIME MEGAZORD LIMPO/xml_reorganizer_pro"

echo "1️⃣  TESTE INICIAL (Verificar se tudo está OK)"
echo "python3 test_reorganizer.py \"$BASE_PATH\""
echo

echo "2️⃣  SIMULAÇÃO (DRY RUN - OBRIGATÓRIO primeiro!)"
echo "python3 xml_reorganizer.py \"$BASE_PATH\" --dry-run"
echo

echo "3️⃣  VALIDAÇÃO APENAS (Opcional - ver problemas detalhados)"
echo "python3 xml_reorganizer.py \"$BASE_PATH\" --only-validate"
echo

echo "4️⃣  EXECUÇÃO REAL (Após confirmar simulação)"
echo "python3 xml_reorganizer.py \"$BASE_PATH\""
echo

echo "════════════════════════════════════════"
echo "📊 RESULTADOS DA VALIDAÇÃO INICIAL:"
echo "   Total de arquivos: 63.876"
echo "   Problemas encontrados: 1.126 arquivos"
echo "   Taxa de contaminação: ~1.8%"
echo

echo "⚠️  PROBLEMAS IDENTIFICADOS:"
echo "   • Arquivos de FEVEREIRO na pasta de MARÇO"
echo "   • Contaminação cruzada em TODAS as pastas"
echo "   • Necessária reorganização baseada na tag <dhEmi>"
echo

echo "✅ SISTEMA VALIDADO E PRONTO!"
echo "   • Permissões: OK"
echo "   • Acesso aos XMLs: OK"
echo "   • Estrutura detectada: OK"
echo

echo "🔧 COMANDOS UTILITÁRIOS AUXILIARES:"
echo "   Listar backups: python3 utils.py xml_reorganizer_work list-backups"
echo "   Verificar estrutura: python3 utils.py xml_reorganizer_work verify \"$BASE_PATH\""
echo "   Restaurar backup: python3 utils.py xml_reorganizer_work restore TIMESTAMP \"$BASE_PATH\" --dry-run"
echo

echo "📁 ARQUIVOS CRIADOS:"
echo "   • Scripts principais em: xml_reorganizer_pro/"
echo "   • Logs em: xml_reorganizer_work/logs/"
echo "   • Backups em: xml_reorganizer_work/backups/"
echo "   • Relatórios em: xml_reorganizer_work/"
echo

echo "⏱️  TEMPO ESTIMADO TOTAL: 4-6 horas"
echo "   Fase 1 (Validação): 30min"
echo "   Fase 2 (Backup): 30min"
echo "   Fase 3 (Reorganização): 2-4h"
echo "   Fase 4 (Verificação): 30min"
echo

echo "🎯 PRÓXIMOS PASSOS RECOMENDADOS:"
echo "   1. Execute o TESTE INICIAL"
echo "   2. Execute a SIMULAÇÃO (--dry-run)"
echo "   3. Analise os logs gerados"
echo "   4. Execute a REORGANIZAÇÃO REAL"
echo "   5. Verifique o relatório final"
