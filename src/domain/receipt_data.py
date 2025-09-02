# receipt_data.py esta clase define el modelo de datos para un recibo

from dataclasses import dataclass

# se usa dataclass para crear una clase de datos inmutable
@dataclass(frozen=True)
class ReceiptData:
    fecha: str
    producto: str
    cantidad: int
    precio: float
    descuento: float

    def __post_init__(self):
        # se validan los datos despues de la inicializacion para asegurar que sean validos
        if self.cantidad < 0:
            raise ValueError("cantidad no puede ser negativa")
        if self.precio < 0:
            raise ValueError("precio no puede ser negativo")
        if self.descuento < 0:
            raise ValueError("descuento no puede ser negativo")

    @property
    def total(self) -> float:
        # esta propiedad calcula el total del recibo
        return (self.precio * self.cantidad) - self.descuento