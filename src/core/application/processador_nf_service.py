from src.core.domain.interfaces import NotaFiscalProcessor
from typing import Any

class ProcessadorNFService:
    """
    Serviço de aplicação para orquestrar o processamento de Notas Fiscais.
    Depende apenas da interface NotaFiscalProcessor (Dependency Inversion).
    """
    def __init__(self, processor: NotaFiscalProcessor):
        self.processor = processor

    def processar_arquivo(self, arquivo_xml: str) -> Any:
        return self.processor.processar(arquivo_xml)

    # Aqui podem ser adicionados outros métodos de orquestração, como processar lotes, etc.
