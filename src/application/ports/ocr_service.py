from abc import ABC, abstractmethod

class OCRService(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """
        Extrae el texto de una imagen utilizando la tecnología OCR.

        Args:
            image_path: La ruta del archivo de imagen.

        Returns:
            Una cadena de texto con el contenido extraído.
        """
        pass