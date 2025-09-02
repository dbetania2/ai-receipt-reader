import io
from google.cloud import vision
from google.oauth2 import service_account
from ...application.ports.ocr_service import OCRService

class CloudVisionOCR(OCRService):
    """
    Implementación de OCRService que utiliza la API de Google Cloud Vision.
    """
    def __init__(self, credentials_path: str):
        """
        Inicializa el cliente de Cloud Vision.

        Args:
            credentials_path: Ruta al archivo JSON de credenciales de la cuenta de servicio.
        """
        # Cargar las credenciales desde el archivo
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = vision.ImageAnnotatorClient(credentials=self.credentials)

    def extract_text(self, image_path: str) -> str:
        """
        Extrae texto de una imagen usando Cloud Vision.

        Args:
            image_path: La ruta al archivo de imagen.

        Returns:
            El texto extraído de la imagen.
        """
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return texts[0].description
            
            if response.error.message:
                print(f"⚠️ Error en Cloud Vision OCR: {response.error.message}")
            
            return ""
        
        except Exception as e:
            print(f"⚠️ Error en CloudVisionOCR: {e}")
            return ""