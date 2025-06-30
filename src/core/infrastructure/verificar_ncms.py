import json

# Carregar a lista oficial
ESPELHO_NCM_MONOFASICA = "/Users/mcplara/Desktop/MAIS ATUALIZADO V12- ZERADO RESETADO ASPIRADO OPTIMUSPRIME MEGAZORD LIMPO/data/tabelas/Espelho de ncms monofásicas.json"

def verificar_ncms_especificos():
    with open(ESPELHO_NCM_MONOFASICA, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
        ncms_monofasicos = set()
        for item in dados:
            if item and "NCMs monofásicos" in item:
                ncm = str(item["NCMs monofásicos"])
                ncms_monofasicos.add(ncm)
    
    # NCMs que apareceram na análise para verificar
    ncms_teste = [
        "30049045",  # PARACETAMOL - deve ser monofásico
        "30039083",  # TENOXICAM - deve ser monofásico
        "30049069",  # CIPROFLOXACINO - deve ser monofásico
        "64022000",  # SANDÁLIAS - deve ser não-monofásico
        "21069030",  # LAVITAN HAIR - deve ser não-monofásico
        "82142000",  # CORTADOR DE UNHA - deve ser não-monofásico
        "34011190",  # TOALHINHAS - pode ser monofásico?
    ]
    
    print("🔍 VERIFICAÇÃO DE NCMs ESPECÍFICOS:")
    print("=" * 50)
    
    for ncm in ncms_teste:
        is_mono = ncm in ncms_monofasicos
        status = "✅ MONOFÁSICO" if is_mono else "❌ NÃO-MONOFÁSICO"
        print(f"NCM {ncm}: {status}")
    
    # Verificar alguns NCMs de medicamentos comuns
    print(f"\n📋 MEDICAMENTOS COMUNS:")
    medicamentos = ["30049045", "30039083", "30049069", "30043933"]
    for ncm in medicamentos:
        is_mono = ncm in ncms_monofasicos
        print(f"  NCM {ncm}: {'SIM' if is_mono else 'NÃO'}")
    
    # Verificar outros produtos
    print(f"\n🛍️ OUTROS PRODUTOS:")
    outros = ["64022000", "21069030", "82142000", "34011190"]
    for ncm in outros:
        is_mono = ncm in ncms_monofasicos
        print(f"  NCM {ncm}: {'MONOFÁSICO' if is_mono else 'NÃO-MONOFÁSICO'}")

if __name__ == "__main__":
    verificar_ncms_especificos()
