# main.py esta clase de encarga de la configuracion y arranque de la aplicacion

from flask import Flask
from dotenv import load_dotenv
import os
import sys

# se anade el directorio src al path del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.controllers.main_controller import main_bp
from src.infrastructure.auth.google_auth import GoogleAuth
from src.infrastructure.gemini.gemini_service_impl import GeminiServiceImpl
from src.infrastructure.ocr.cloud_vision_ocr import CloudVisionOCR
from src.application.usecases.receipt_processing_service import ReceiptProcessingService

# se cargan las variables de entorno desde el archivo .env
load_dotenv()

# esta funcion crea y configura la aplicacion flask
def create_app():
    app = Flask(__name__)
    # se obtiene la clave secreta para la sesion
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")

    # se obtiene la url del servidor
    server_url = os.environ.get("SERVER_URL")

    # se obtienen las credenciales y la api key
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # se inicializan los servicios necesarios
    ocr_service = CloudVisionOCR(credentials_path=credentials_path)
    gemini_service = GeminiServiceImpl(api_key=gemini_api_key)
    google_auth_service = GoogleAuth(auth_url=server_url)

    # se inicializa el servicio principal de procesamiento de recibos
    receipt_processor = ReceiptProcessingService(
        ocr_service=ocr_service,
        gemini_service=gemini_service
    )

    # se inyectan los servicios en el blueprint para su uso
    main_bp.receipt_processor = receipt_processor
    main_bp.google_auth_service = google_auth_service
    main_bp.gemini_service = gemini_service

    # se registra el blueprint en la aplicacion
    app.register_blueprint(main_bp)

    return app

# este bloque se ejecuta solo si el script es el principal
if __name__ == '__main__':
    # .\.venv\Scripts\activate
    app = create_app()
    app.run(port=5000, debug=True)