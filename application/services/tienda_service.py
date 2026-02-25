"""
CAPA: Application / Services
==============================
Orquesta los 3 patrones para ejecutar la lógica de negocio.

  LógicaService usa:
  → SINGLETON  : ConfiguracionTienda  (validar, generar IDs)
  → FACTORY    : ProductoFactory      (crear manejador de producto)
  → ADAPTER    : obtener_pasarela()   (procesar pago con cualquier pasarela)
"""

from domain.model.modelos import Producto, Pedido, ItemPedido
from infrastructure.config.configuracion import ConfiguracionTienda
from infrastructure.factory.producto_factory import ProductoFactory
from infrastructure.adapters.adapters_pago import obtener_pasarela


class TiendaService:
    """Servicio principal de la tienda de videojuegos."""

    def __init__(self):
        # SINGLETON: única instancia de configuración
        self._config = ConfiguracionTienda()
        self._catalogo: list[Producto]  = []
        self._pedidos:  list[Pedido]    = []
        self._carrito:  list[ItemPedido] = []
        self._cliente_actual: str = ""
        self._cargar_catalogo_demo()

    # ── Catálogo ──────────────────────────────────────────

    def _cargar_catalogo_demo(self):
        """Carga productos de ejemplo al iniciar."""
        productos = [
            Producto("G001", "Elden Ring",            "RPG",      "PC",              199.90, "DIGITAL",     999),
            Producto("G002", "FIFA 25",                "Deportes", "PS5",             249.90, "FISICO",       15),
            Producto("G003", "The Legend of Zelda",   "Aventura", "Nintendo Switch",  299.90, "FISICO",        8),
            Producto("G004", "Call of Duty: MW3",     "Acción",   "Xbox",            189.90, "DIGITAL",     999),
            Producto("G005", "Cyberpunk 2077",        "RPG",      "PC",               99.90, "DIGITAL",     999),
            Producto("G006", "Phantom Liberty DLC",   "RPG",      "PC",               69.90, "DLC",         999),
            Producto("G007", "Game Pass Ultimate 1m", "—",        "Xbox/PC",          34.90, "SUSCRIPCION", 999),
            Producto("G008", "Game Pass Ultimate 3m", "—",        "Xbox/PC",          89.90, "SUSCRIPCION", 999),
            Producto("G009", "PS Plus Extra 12m",     "—",        "PS5/PS4",         269.90, "SUSCRIPCION", 999),
            Producto("G010", "Spider-Man 2",          "Acción",   "PS5",             299.90, "FISICO",        5),
        ]
        self._catalogo = productos

    def listar_catalogo(self, filtro_tipo: str = "") -> list[Producto]:
        if filtro_tipo:
            return [p for p in self._catalogo if p.tipo == filtro_tipo.upper()]
        return self._catalogo

    def buscar_producto(self, id_producto: str) -> Producto | None:
        return next((p for p in self._catalogo if p.id == id_producto.upper()), None)

    # ── Carrito ───────────────────────────────────────────

    def set_cliente(self, nombre: str):
        self._cliente_actual = nombre
        self._carrito = []

    def agregar_al_carrito(self, id_producto: str, cantidad: int) -> tuple[bool, str]:
        producto = self.buscar_producto(id_producto)
        if not producto:
            return False, f"Producto '{id_producto}' no encontrado."

        # FACTORY: crea el manejador correcto para este tipo de producto
        manejador = ProductoFactory.crear(producto)

        # Validar compra con las reglas del tipo
        valido, mensaje = manejador.validar_compra(cantidad)
        if not valido:
            return False, mensaje

        # Verificar si ya está en el carrito
        for item in self._carrito:
            if item.producto.id == id_producto:
                item.cantidad += cantidad
                return True, f"Cantidad actualizada: {item.cantidad}x {producto.nombre}"

        self._carrito.append(ItemPedido(producto, cantidad, producto.precio))
        return True, f"✅ Agregado: {cantidad}x {producto.nombre}"

    def ver_carrito(self) -> list[ItemPedido]:
        return self._carrito

    def total_carrito(self) -> float:
        return sum(item.subtotal for item in self._carrito)

    def vaciar_carrito(self):
        self._carrito = []

    # ── Pedido y pago ─────────────────────────────────────

    def crear_pedido(self) -> Pedido | None:
        if not self._carrito:
            return None
        if not self._cliente_actual:
            return None

        # SINGLETON: genera el ID de pedido
        id_pedido = self._config.generar_id_pedido()
        pedido = Pedido(
            id       = id_pedido,
            cliente  = self._cliente_actual,
            items    = self._carrito.copy(),
        )
        return pedido

    def procesar_pago(self, pedido: Pedido, metodo: str) -> tuple[bool, str]:
        """
        Procesa el pago usando la pasarela seleccionada.
        ADAPTER: obtener_pasarela() devuelve el adaptador correcto.
        """
        if not self._config.pasarela_activa(metodo):
            return False, f"Pasarela '{metodo}' no disponible en esta tienda."

        # ADAPTER: selecciona y retorna el adaptador correcto
        pasarela = obtener_pasarela(metodo)
        moneda   = self._config.obtener("moneda")

        resultado = pasarela.cobrar(pedido, moneda)

        if resultado["exitoso"]:
            pedido.estado         = "PAGADO"
            pedido.metodo_pago    = metodo
            pedido.id_transaccion = resultado["id_transaccion"]
            self._pedidos.append(pedido)

            # FACTORY: ejecuta post_compra para cada producto
            print("\n  📬 Procesando entrega:")
            for item in pedido.items:
                manejador = ProductoFactory.crear(item.producto)
                manejador.post_compra(pedido)

            self._carrito = []
            return True, resultado["mensaje"]

        return False, "El pago no pudo procesarse. Intenta con otro método."

    # ── Historial ─────────────────────────────────────────

    def historial_pedidos(self) -> list[Pedido]:
        return self._pedidos
