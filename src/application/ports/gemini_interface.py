from abc import ABC, abstractmethod
from typing import Dict

class GeminiInterface(ABC):
    @abstractmethod
    def process_text_from_receipt(self, receipt_text: str) -> Dict:
        """
        Procesa el texto extraído de un recibo utilizando el modelo de IA de Gemini.

        Args:
            receipt_text: El texto completo extraído del recibo.

        Returns:
            Un diccionario con los datos estructurados del recibo.
        """
        pass