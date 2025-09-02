# src/application/usecases/receipt_processing_service.py

from typing import List, Dict
from ..ports.ocr_service import OCRService
from ..ports.gemini_interface import GeminiInterface
from ...domain.receipt_data import ReceiptData
from .receipt_processing_result import ReceiptProcessingResult
import json
import re

class ReceiptProcessingService:
    def __init__(self, ocr_service: OCRService, gemini_service: GeminiInterface):
        self.ocr_service = ocr_service
        self.gemini_service = gemini_service

    def process_receipt(self, image_path: str) -> ReceiptProcessingResult:
        """
        Procesa la imagen de un recibo para extraer y estructurar los datos.

        Args:
            image_path: La ruta al archivo de imagen del recibo.

        Returns:
            Un objeto ReceiptProcessingResult con los datos del recibo o None si falla.
        """
        try:
            raw_text = self.ocr_service.extract_text(image_path)

            if not raw_text or raw_text.strip() == "":
                print("⚠️ Error en OCR. No se puede procesar.")
                return None

            # Procesamos el texto con Gemini para obtener el JSON estructurado
            structured_data = self.gemini_service.process_text_from_receipt(raw_text)
            
            # Convertimos el diccionario a un objeto ReceiptProcessingResult
            return self._convert_dict_to_receipt_result(structured_data)

        except Exception as e:
            print(f"⚠️ Error general en procesamiento: {e}")
            return None

    def _convert_dict_to_receipt_result(self, data: Dict) -> ReceiptProcessingResult:
        """
        Método auxiliar para convertir un diccionario en un objeto ReceiptProcessingResult.
        """
        try:
            receipt_data_list = []
            total = data.get("total", 0.0)
            fecha = data.get("fecha", "")
            productos = data.get("productos", [])

            for prod in productos:
                receipt_data_list.append(ReceiptData(
                    fecha=fecha,
                    producto=prod.get("nombre", ""),
                    cantidad=prod.get("cantidad", 0),
                    precio=prod.get("precio_unitario", 0.0),
                    descuento=0.0 # Asumimos 0.0 ya que el prompt de Gemini no lo extrae
                ))
            
            return ReceiptProcessingResult(receipt_data_list=receipt_data_list, total=total)
        
        except (ValueError, KeyError) as e:
            print(f"⚠️ Error convirtiendo diccionario: {e}")
            return None
