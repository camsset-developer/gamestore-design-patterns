"""
CAPA: Domain / Model
=====================
Entidades puras del negocio. No dependen de nada externo.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Producto:
    """Representa un producto en el catálogo de la tienda."""
    id: str
    nombre: str
    genero: str           # "Acción", "RPG", "Deportes", etc.
    plataforma: str       # "PC", "PS5", "Xbox", "Nintendo Switch"
    precio: float
    tipo: str             # "FISICO", "DIGITAL", "DLC", "SUSCRIPCION"
    stock: int = 0
    descripcion: str = ""

    def __str__(self):
        stock_txt = f"Stock: {self.stock}" if self.tipo == "FISICO" else "Descarga"
        return (f"[{self.id}] {self.nombre} | {self.plataforma} | "
                f"S/ {self.precio:.2f} | {self.tipo} | {stock_txt}")


@dataclass
class ItemPedido:
    """Un producto dentro de un pedido con su cantidad."""
    producto: Producto
    cantidad: int
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        return self.precio_unitario * self.cantidad


@dataclass
class Pedido:
    """Representa un pedido del cliente."""
    id: str
    cliente: str
    items: list = field(default_factory=list)
    estado: str = "PENDIENTE"       # PENDIENTE | PAGADO | CANCELADO
    metodo_pago: str = ""
    id_transaccion: str = ""
    fecha: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def mostrar(self):
        print(f"\n  🛒 Pedido: {self.id} | Cliente: {self.cliente} | Estado: {self.estado}")
        print(f"     {'Producto':<30} {'Cant':>5} {'P.Unit':>8} {'Subtotal':>10}")
        print(f"     {'─'*56}")
        for item in self.items:
            print(f"     {item.producto.nombre:<30} {item.cantidad:>5} "
                  f"S/{item.precio_unitario:>7.2f} S/{item.subtotal:>9.2f}")
        print(f"     {'─'*56}")
        print(f"     {'TOTAL':>44} S/{self.total:>9.2f}")
        if self.id_transaccion:
            print(f"     Transacción: {self.id_transaccion} | Método: {self.metodo_pago}")
