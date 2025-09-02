from ...application.ports.ocr_service import OCRService
import pytesseract
from PIL import Image

class TesseractOCR(OCRService):
    """
    Implementación de OCRService que utiliza Tesseract OCR de forma local.
    """
    def __init__(self, tessdata_path: str, language: str = 'spa'):
        """
        Inicializa la configuración de Tesseract.
        
        Args:
            tessdata_path: Ruta al directorio que contiene la carpeta 'tessdata'.
            language: Código del idioma a usar (por defecto 'spa' para español).
        """
        self.tesseract = pytesseract
        self.tesseract.tesseract_cmd = 'tesseract'  # Asegúrate de que Tesseract esté en el PATH
        self.tesseract_config = f'--tessdata-dir "{tessdata_path}"'
        self.language = language

    def extract_text(self, image_path: str) -> str:
        """
        Extrae texto de una imagen usando Tesseract.

        Args:
            image_path: La ruta al archivo de imagen.

        Returns:
            El texto extraído de la imagen.
        """
        try:
            image = Image.open(image_path)
            # Usa el método `image_to_string` para procesar la imagen
            text = self.tesseract.image_to_string(image, lang=self.language, config=self.tesseract_config)
            return text
        except Exception as e:
            print(f"⚠️ Error en TesseractOCR: {e}")
            return ""