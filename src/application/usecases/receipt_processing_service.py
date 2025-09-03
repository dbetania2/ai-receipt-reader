# src/application/usecases/receipt_processing_service.py

from typing import List, Dict
from ..ports.ocr_service import OCRService
from ..ports.gemini_interface import GeminiInterface
from ...domain.receipt_data import ReceiptData
from .receipt_processing_result import ReceiptProcessingResult
from datetime import datetime, timedelta
import json
import os

class ReceiptProcessingService:
    def __init__(self, ocr_service: OCRService, gemini_service: GeminiInterface):
        self.ocr_service = ocr_service
        self.gemini_service = gemini_service

        # Carpeta para guardar logs intermedios
        self.debug_folder = "receipt_debug"
        # os.makedirs(self.debug_folder, exist_ok=True)  # 👈 Solo para pruebas, comentar en producción

    def process_receipt(self, image_path: str) -> ReceiptProcessingResult:
        """
        Procesa la imagen de un recibo para extraer y estructurar los datos,
        guardando archivos de depuración con el texto crudo, JSON de Gemini
        y resultado final normalizado.
        """
        try:
            # 1️⃣ Texto crudo desde Cloud Vision
            raw_text = self.ocr_service.extract_text(image_path)
            raw_file = os.path.join(self.debug_folder, "raw_text.txt")
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(raw_text or "")
            print(f"🔹 Texto crudo guardado en {raw_file}")

            if not raw_text or raw_text.strip() == "":
                print("⚠️ Error en Cloud Vision. No se puede procesar.")
                return None

            # 2️⃣ JSON devuelto por Gemini
            structured_data = self.gemini_service.process_text_from_receipt(raw_text)
            gemini_file = os.path.join(self.debug_folder, "gemini_output.json")
            with open(gemini_file, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            print(f"🔹 JSON de Gemini guardado en {gemini_file}")

            # 3️⃣ Resultado final normalizado
            result = self._convert_dict_to_receipt_result(structured_data)
            if result is not None:
                normalized_file = os.path.join(self.debug_folder, "normalized_output.json")
                normalized_data = {
                    "receipt_data": [vars(r) for r in result.receipt_data_list],
                    "total": result.total
                }
                with open(normalized_file, "w", encoding="utf-8") as f:
                    json.dump(normalized_data, f, indent=2, ensure_ascii=False)
                print(f"🔹 Resultado final normalizado guardado en {normalized_file}")
            else:
                print("⚠️ No se pudo normalizar el resultado.")

            return result

        except Exception as e:
            print(f"⚠️ Error general en procesamiento: {e}")
            return None

    def _convert_dict_to_receipt_result(self, data: Dict) -> ReceiptProcessingResult:
        """
        Convierte un diccionario en un objeto ReceiptProcessingResult.
        Normaliza la fecha raíz y asegura que todos los productos sean válidos.
        """
        def normalize_fecha(fecha_val) -> str:
            """
            Convierte cualquier fecha a formato dd/mm/yyyy.
            Maneja números tipo Excel (int, float o string) y strings dd/mm/yyyy.
            Devuelve None si no se puede convertir.
            """
            if fecha_val is None:
                return None
            try:
                numero = int(float(fecha_val))
                fecha = datetime(1899, 12, 30) + timedelta(days=numero)
                return fecha.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                pass

            try:
                fecha_str = str(fecha_val).strip()
                datetime.strptime(fecha_str, "%d/%m/%Y")
                return fecha_str
            except (ValueError, TypeError):
                pass

            return None

        receipt_data_list = []
        total = data.get("total_general", 0.0)

        # Normalizamos solo la fecha raíz
        fecha_raiz = normalize_fecha(data.get("fecha"))
        if fecha_raiz is None:
            print("⚠️ No se pudo determinar la fecha del recibo. Revisar OCR/Gemini.")
            return None

        productos = data.get("productos", [])

        for prod in productos:
            try:
                # Cantidad como int
                try:
                    cantidad = int(float(prod.get("cantidad", 1)))
                    if cantidad <= 0:
                        cantidad = 1
                except (ValueError, TypeError):
                    cantidad = 1

                # Precio como float
                try:
                    precio = round(float(prod.get("precio_unitario", 0.0)), 2)
                except (ValueError, TypeError):
                    precio = 0.0

                # Nombre seguro
                nombre = str(prod.get("nombre", "")).strip()

                # Todos los productos usan la misma fecha raíz
                receipt_data_list.append(ReceiptData(
                    fecha=fecha_raiz,
                    producto=nombre,
                    cantidad=cantidad,
                    precio=precio,
                    descuento=0.0
                ))
            except Exception as e:
                print(f"⚠️ Error con producto {prod}: {e}")
                continue

        return ReceiptProcessingResult(
            receipt_data_list=receipt_data_list,
            total=round(float(total), 2)
        )
