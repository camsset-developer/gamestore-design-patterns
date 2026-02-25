"""
CAPA: Infrastructure / Factory
================================
PATRÓN: FACTORY METHOD
========================
Crea el tipo correcto de producto según su categoría.
Cada tipo tiene sus propias reglas de validación y post-compra.

El servicio nunca instancia productos directamente:
    ProductoFactory.crear(producto_data)  →  ProductoFisico | ProductoDigital | ...
"""

from domain.interfaces.interfaces import IProducto
from domain.model.modelos import Producto, Pedido


# ════════════════════════════════════════════════════
# PRODUCTOS CONCRETOS — cada uno con sus propias reglas
# ════════════════════════════════════════════════════

class ProductoFisico(IProducto):
    """
    Juego en formato físico (caja, disco).
    Tiene stock limitado y se descuenta al comprar.
    """
    def __init__(self, producto: Producto):
        self._producto = producto

    def tipo(self) -> str:
        return "FISICO"

    def validar_compra(self, cantidad: int) -> tuple[bool, str]:
        if self._producto.stock <= 0:
            return False, f"'{self._producto.nombre}' sin stock disponible."
        if cantidad > self._producto.stock:
            return False, (f"Stock insuficiente. Disponible: {self._producto.stock}, "
                           f"solicitado: {cantidad}.")
        return True, ""

    def post_compra(self, pedido: Pedido):
        for item in pedido.items:
            if item.producto.id == self._producto.id:
                self._producto.stock -= item.cantidad
                print(f"     📦 Stock actualizado: {self._producto.nombre} "
                      f"→ {self._producto.stock} unidades restantes.")


class ProductoDigital(IProducto):
    """
    Juego descargable (Steam, PSN, eShop).
    Sin stock físico, entrega instantánea de clave de activación.
    """
    def __init__(self, producto: Producto):
        self._producto = producto

    def tipo(self) -> str:
        return "DIGITAL"

    def validar_compra(self, cantidad: int) -> tuple[bool, str]:
        if cantidad > 5:
            return False, "Máximo 5 copias digitales por pedido."
        return True, ""

    def post_compra(self, pedido: Pedido):
        import random, string
        clave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        clave_fmt = '-'.join([clave[i:i+4] for i in range(0, 16, 4)])
        print(f"     🔑 Clave de activación generada: {clave_fmt}")
        print(f"        Juego: {self._producto.nombre} | Plataforma: {self._producto.plataforma}")


class ProductoDLC(IProducto):
    """
    Contenido descargable adicional (expansiones, skins, pases de temporada).
    Requiere juego base instalado.
    """
    def __init__(self, producto: Producto):
        self._producto = producto

    def tipo(self) -> str:
        return "DLC"

    def validar_compra(self, cantidad: int) -> tuple[bool, str]:
        if cantidad > 1:
            return False, "Solo se puede comprar 1 unidad de DLC por pedido."
        return True, ""

    def post_compra(self, pedido: Pedido):
        print(f"     🎮 DLC activado: {self._producto.nombre}")
        print(f"        Se añadirá automáticamente a tu biblioteca.")


class ProductoSuscripcion(IProducto):
    """
    Suscripción mensual/anual (Game Pass, PS Plus, Nintendo Online).
    Sin límite de cantidad, se activa por días según plan.
    """
    _duraciones = {"1 mes": 30, "3 meses": 90, "12 meses": 365}

    def __init__(self, producto: Producto):
        self._producto = producto

    def tipo(self) -> str:
        return "SUSCRIPCION"

    def validar_compra(self, cantidad: int) -> tuple[bool, str]:
        return True, ""

    def post_compra(self, pedido: Pedido):
        nombre = self._producto.nombre
        dias = next((v for k, v in self._duraciones.items() if k in nombre), 30)
        print(f"     ⭐ Suscripción activada: {nombre}")
        print(f"        Duración: {dias} días de acceso premium.")


# ════════════════════════════════════════════════════
# FACTORY — Decide qué clase concreta crear
# ════════════════════════════════════════════════════

class ProductoFactory:
    """
    Fábrica de productos.

    Recibe un objeto Producto con su tipo definido y
    retorna la instancia IProducto correcta con sus reglas.

    El servicio llama:
        ProductoFactory.crear(producto)
    Y obtiene el manejador correcto sin conocer las clases concretas.
    """

    _registro = {
        "FISICO":      ProductoFisico,
        "DIGITAL":     ProductoDigital,
        "DLC":         ProductoDLC,
        "SUSCRIPCION": ProductoSuscripcion,
    }

    @classmethod
    def crear(cls, producto: Producto) -> IProducto:
        """
        Crea y retorna el manejador de producto según su tipo.

        Args:
            producto: Entidad Producto con tipo definido

        Returns:
            IProducto concreto listo para validar y procesar
        """
        tipo = producto.tipo.upper()
        if tipo not in cls._registro:
            disponibles = ", ".join(cls._registro.keys())
            raise ValueError(
                f"Tipo '{tipo}' no reconocido. Disponibles: {disponibles}"
            )
        clase = cls._registro[tipo]
        print(f"  🏭 [FACTORY] Tipo '{tipo}' → {clase.__name__}")
        return clase(producto)

    @classmethod
    def tipos_disponibles(cls) -> list:
        return list(cls._registro.keys())
