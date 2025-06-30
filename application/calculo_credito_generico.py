import sys
sys.path.append('src')
from core.domain.tabelas import obter_parametros_simples, calcular_selic_acumulada

def calcular_credito_generico(rbt12, receita_nao_mono, pis_declarado, cofins_declarado, periodo, cliente_nome=None):
    """
    Calcula crédito/debito atualizado para qualquer cliente e período.
    Args:
        rbt12: Receita bruta acumulada 12 meses
        receita_nao_mono: Receita não monofásica do período
        pis_declarado: Valor de PIS declarado
        cofins_declarado: Valor de COFINS declarado
        periodo: string AAAA-MM
        cliente_nome: opcional, nome do cliente para exibir no print
    """
    aliquota, valor_deduzir = obter_parametros_simples(rbt12)
    aliquota_efetiva = (rbt12 * aliquota - valor_deduzir) / rbt12
    pis_prop = 0.0276
    cofins_prop = 0.1274
    pis_efetivo = aliquota_efetiva * pis_prop
    cofins_efetivo = aliquota_efetiva * cofins_prop
    pis_devido = receita_nao_mono * pis_efetivo
    cofins_devido = receita_nao_mono * cofins_efetivo
    credito_total = (pis_declarado + cofins_declarado) - (pis_devido + cofins_devido)
    fator_selic = calcular_selic_acumulada(periodo)
    credito_atualizado = credito_total * fator_selic
    if cliente_nome:
        print(f"\n📊 {cliente_nome.upper()} - {periodo} (METODOLOGIA GENÉRICA)")
    else:
        print(f"\n📊 RESULTADO - {periodo} (METODOLOGIA GENÉRICA)")
    print(f"RBT12: R$ {rbt12:,.2f}")
    print(f"Alíquota efetiva: {aliquota_efetiva*100:.4f}%")
    print(f"Débito: R$ {abs(credito_total):.2f}")
    print(f"Débito atualizado SELIC: R$ {abs(credito_atualizado):.2f}")
    return credito_atualizado

if __name__ == "__main__":
    # Exemplo de uso genérico (substitua pelos dados do cliente desejado)
    resultado = calcular_credito_generico(
        rbt12=0,  # informe o valor
        receita_nao_mono=0,  # informe o valor
        pis_declarado=0,  # informe o valor
        cofins_declarado=0,  # informe o valor
        periodo="2025-03",  # informe o período
        cliente_nome="CLIENTE"
    )
