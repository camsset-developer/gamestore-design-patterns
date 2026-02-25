"""
CAPA: Domain / Interfaces
==========================
Contratos abstractos que definen QUÉ debe hacer cada componente,
sin decir CÓMO lo hace. Ninguna capa superior depende de
implementaciones concretas, solo de estas interfaces.
"""
from abc import ABC, abstractmethod
from domain.model.modelos import Producto, Pedido


class IProducto(ABC):
    """
    Contrato para cualquier tipo de producto de la tienda.
    Usado por el patrón FACTORY para crear productos concretos.
    """

    @abstractmethod
    def tipo(self) -> str:
        """Retorna el tipo: FISICO, DIGITAL, DLC, SUSCRIPCION."""
        pass

    @abstractmethod
    def validar_compra(self, cantidad: int) -> tuple[bool, str]:
        """
        Valida si la compra es posible.
        Retorna (True, "") si ok, o (False, "razón") si no.
        """
        pass

    @abstractmethod
    def post_compra(self, pedido: Pedido):
        """Acciones después de confirmar la compra (ej: descontar stock)."""
        pass


class IPasarelaPago(ABC):
    """
    Contrato estándar para cualquier pasarela de pago.
    Usado por el patrón ADAPTER para unificar APIs externas.
    """

    @abstractmethod
    def cobrar(self, pedido: Pedido, moneda: str) -> dict:
        """
        Procesa el cobro del pedido.
        Retorna dict con: exitoso, id_transaccion, mensaje
        """
        pass

    @abstractmethod
    def verificar(self, id_transaccion: str) -> dict:
        """Consulta el estado de una transacción."""
        pass

    @abstractmethod
    def nombre(self) -> str:
        """Nombre de la pasarela."""
        pass
