from abc import ABC, abstractmethod
from typing import Any

class NotaFiscalProcessor(ABC):
    """
    Interface para processadores de Nota Fiscal Eletrônica (NF-e).
    Qualquer processador de NF-e deve implementar este contrato.
    """
    @abstractmethod
    def processar(self, arquivo_xml: str) -> Any:
        """
        Processa um arquivo XML de NF-e e retorna o resultado do processamento.
        Args:
            arquivo_xml: Caminho para o arquivo XML da nota fiscal.
        Returns:
            Qualquer resultado relevante do processamento (dict, objeto, etc).
        """
        pass
