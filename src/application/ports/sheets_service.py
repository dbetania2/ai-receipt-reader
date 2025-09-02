from abc import ABC, abstractmethod
from typing import List
from ...domain.receipt_data import ReceiptData

class SheetsService(ABC):
    @abstractmethod
    def save_receipt_data(self, data: List[ReceiptData]):
        """
        Guarda una lista de datos de recibos en una hoja de cálculo.

        Args:
            data: Una lista de objetos ReceiptData.
        """
        pass