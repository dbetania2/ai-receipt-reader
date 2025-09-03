# src/infrastructure/gemini/gemini_service_impl.py

import os
import json
from typing import Dict, Any
from google.generativeai.types import GenerationConfig
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from ...application.ports.gemini_interface import GeminiInterface
from datetime import datetime

class GeminiServiceImpl(GeminiInterface):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process_text_from_receipt(self, receipt_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extrae la información de un recibo y devuélvela en un JSON válido.  

        JSON requerido:

        {{
            "fecha": "fecha única del recibo en formato dd/mm/yyyy",
            "productos": [
                {{
                    "nombre": "nombre del producto",
                    "cantidad": cantidad del producto (int),
                    "precio_unitario": precio unitario del producto (float, 2 decimales)
                }}
            ],
            "total_general": precio total del recibo (float, 2 decimales)
        }}

        Instrucciones clave:
        - Todos los productos deben usar la **misma fecha**, que será la fecha del ticket.
        - Si aparece un número tipo Excel (ej: 45901), conviértelo automáticamente a dd/mm/yyyy.
        - Si hay múltiples fechas detectadas en el ticket, determina la más probable como fecha principal y úsala para todos los productos.
        - No uses valores por defecto como "01/09/2025"; si no se puede determinar, deja el campo "fecha" vacío.
        - El campo "cantidad" debe ser int; si falta, asumir 1.
        - El campo "precio_unitario" debe ser float con 2 decimales.
        - El campo "total_general" debe reflejar la suma real de todos los productos.

        Texto del recibo:
        {receipt_text}
        """

        try:
            generation_config = GenerationConfig(
                response_mime_type="application/json"
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            json_data = json.loads(response.text)
            return json_data

        except Exception as e:
            print(f"⚠️ Error al procesar el texto con Gemini: {e}")
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            return {"fecha": fecha_actual, "productos": [], "total_general": 0.0}
