#!/usr/bin/env python3
"""
Verificar valores a serem recuperados - CHISTE SAMPAIO
"""

import os
import sys
import json

# Adicionar diretório src ao path
sys.path.append('src')

def verificar_valores_recuperacao():
    """
    Verifica se há valores de PIS/COFINS a serem recuperados
    """
    print("💰 VERIFICAÇÃO DE VALORES A RECUPERAR - CHISTE SAMPAIO")
    print("=" * 60)
    
    # Dados processados dos XMLs
    valor_xmls_fev = 111626.42
    ncm_principal = "21050010"
    print(f"📊 Valor processado XMLs Fevereiro: R$ {valor_xmls_fev:,.2f}")
    print(f"🏷️ NCM Principal: {ncm_principal} (Sorvetes)")
    
    # Verificar se NCM é monofásico
    try:
        from core.domain.tabelas import verificar_ncm_monofasico
        eh_monofasico = verificar_ncm_monofasico(ncm_principal)
        print(f"🔍 NCM {ncm_principal} é monofásico? {eh_monofasico}")
    except Exception as e:
        print(f"❌ Erro ao verificar NCM: {e}")
        return
    
    if eh_monofasico:
        print("\n✅ PRODUTO MONOFÁSICO IDENTIFICADO!")
        print("💡 Regra: PIS/COFINS = ZERO para produtos monofásicos")
        print("💰 Crédito = Todo PIS/COFINS declarado no PGDAS")
        
        # Tentar carregar dados do PGDAS se existir
        pgdas_paths = [
            "/Users/mcplara/Desktop/BUMERANGUE/DADOS CLIENTES/SOL E NEVE/PGDAS/chiste sampaio/CHISTE SAMPAIO EXTRATO DO SIMPLES 02.2025.pdf"
        ]
        
        print(f"\n📋 Para calcular crédito exato, precisamos dos valores de PIS/COFINS do PGDAS:")
        for path in pgdas_paths:
            if os.path.exists(path):
                print(f"✅ PGDAS encontrado: {os.path.basename(path)}")
            else:
                print(f"❌ PGDAS não encontrado: {os.path.basename(path)}")
        
        print(f"\n🎯 FÓRMULA PARA CÁLCULO:")
        print(f"Crédito = PIS declarado + COFINS declarado")
        print(f"Motivo: Como sorvetes são monofásicos, PIS/COFINS devidos = R$ 0,00")
        
    else:
        print("\n❌ PRODUTO NÃO É MONOFÁSICO")
        print("📋 Resultado: NÃO HÁ VALORES A RECUPERAR")
        print("💡 Explicação: Como não é monofásico, PIS/COFINS são devidos normalmente")
        print("🎯 Valor a recuperar: R$ 0,00")
    
    return eh_monofasico

def main():
    """
    Função principal
    """
    resultado = verificar_valores_recuperacao()
    
    print(f"\n" + "="*60)
    if resultado:
        print("🎯 CONCLUSÃO: HÁ POTENCIAL DE RECUPERAÇÃO")
        print("📋 PRÓXIMO PASSO: Analisar PGDAS para valor exato")
    else:
        print("🎯 CONCLUSÃO: NÃO HÁ VALORES A RECUPERAR")
        print("📋 MOTIVO: Produto não é monofásico")
    print("="*60)

if __name__ == "__main__":
    main()
