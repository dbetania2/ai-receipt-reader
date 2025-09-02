# gemini_service_impl.py esta clase implementa la interfaz de gemini para procesar recibos

import os
import json
from typing import Dict, Any
from google.generativeai.types import GenerationConfig
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from ...application.ports.gemini_interface import GeminiInterface


class GeminiServiceImpl(GeminiInterface):
    """
    implementacion del servicio de gemini que se comunica directamente con la api
    esta clase implementa la interfaz geminiinterface
    """
    def __init__(self, api_key: str):
        """
        inicializa el servicio con la clave de la api de gemini
        
        args:
            api_key: la clave de la api de gemini
        """
        # se configura la api de gemini con la clave
        genai.configure(api_key=api_key)
        # se inicializa el modelo gemini 1.5 flash
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process_text_from_receipt(self, receipt_text: str) -> Dict[str, Any]:
        """
        procesa el texto extraido de un recibo usando la api de gemini
        
        args:
            receipt_text: el texto completo extraido del recibo
        
        returns:
            un diccionario con los datos estructurados del recibo o un diccionario vacio en caso de error
        """
        # se define el prompt para extraer informacion en formato json
        prompt = f"""
        extrae la siguiente informacion de un recibo. los datos deben ser devueltos en formato json

        el json debe tener la siguiente estructura:

        {{
            "fecha": "fecha del recibo en formato dd/mm/aaaa",
            "productos": [
                {{
                    "nombre": "nombre del producto",
                    "cantidad": cantidad del producto (int),
                    "precio_unitario": precio unitario del producto (float)
                }}
            ],
            "total": precio total del recibo (float)
        }}

        instrucciones:
        - si un producto no tiene cantidad explicita (e.g., "la senisima $19.00"), asume que la cantidad es 1
        - si el formato es "2x #19.00", la cantidad es 2 y el precio unitario es 19.00
        - para la fecha, usa el formato dd/mm/aaaa

        texto del recibo:
        {receipt_text}
        """

        try:
            # se configura la respuesta para que sea en formato json
            generation_config = GenerationConfig(
                response_mime_type="application/json"
            )
            
            # se envia el prompt al modelo para generar contenido
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

            # se parsea el texto de la respuesta a json
            json_data = json.loads(response.text)
            return json_data
        except Exception as e:
            # se maneja cualquier error durante el procesamiento
            print(f"error al procesar el texto con gemini: {e}")
            return {"fecha": "", "productos": [], "total": 0.0}