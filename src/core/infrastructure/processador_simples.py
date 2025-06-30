from src.core.domain.interfaces import NotaFiscalProcessor

class ProcessadorSimples(NotaFiscalProcessor):
    def processar(self, arquivo_xml: str) -> dict:
        # Aqui você implementaria a lógica real de processamento
        # Exemplo fictício:
        return {"arquivo": arquivo_xml, "status": "processado"}
