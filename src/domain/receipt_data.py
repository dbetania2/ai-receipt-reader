from dataclasses import dataclass

@dataclass(frozen=True)
class ReceiptData:
    fecha: str
    producto: str
    cantidad: int
    precio: float
    descuento: float

    def __post_init__(self):
        if self.cantidad < 0:
            raise ValueError("cantidad no puede ser negativa")
        if self.precio < 0:
            raise ValueError("precio no puede ser negativo")
        if self.descuento < 0:
            raise ValueError("descuento no puede ser negativo")

    @property
    def total(self) -> float:
        return (self.precio * self.cantidad) - self.descuento
