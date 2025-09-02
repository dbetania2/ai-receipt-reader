from dataclasses import dataclass
from typing import List
from domain.receipt_data import ReceiptData

@dataclass(frozen=True)
class ReceiptProcessingResult:
    """
    Contiene los resultados del procesamiento de un recibo.
    """
    receipt_data_list: List[ReceiptData]
    total: float