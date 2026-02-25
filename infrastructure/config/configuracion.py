"""
CAPA: Infrastructure / Config
================================
PATRÓN: SINGLETON
==================
Configuración global de la tienda. Una sola instancia
garantiza que todos los módulos lean los mismos parámetros
sin inconsistencias ni duplicados.
"""


class ConfiguracionTienda:
    """
    Singleton que gestiona la configuración global de GameStore.

    Ejemplos de uso en la app:
    - La Factory lo consulta para saber qué tipos de producto están activos.
    - El Service lo usa para generar IDs de pedido y validar moneda.
    - El menú lo muestra en la opción "Configuración".
    """

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._init_config()
            print("  ✅ [SINGLETON] ConfiguracionTienda creada — única instancia.")
        return cls._instancia

    def _init_config(self):
        self._config = {
            "nombre_tienda":      "GameStore Perú",
            "version":            "3.0.0",
            "moneda":             "PEN",
            "simbolo_moneda":     "S/",
            "igv":                0.18,
            "tipos_activos":      ["FISICO", "DIGITAL", "DLC", "SUSCRIPCION"],
            "pasarelas_activas":  ["PAYPAL", "CULQI", "YAPE"],
            "max_items_pedido":   10,
            "prefijo_pedido":     "ORD",
        }
        self._correlativo_pedido = 1

    # ── Acceso general ────────────────────────────────────
    def obtener(self, clave: str):
        return self._config.get(clave)

    def establecer(self, clave: str, valor):
        self._config[clave] = valor

    def mostrar(self):
        print(f"\n  ⚙️  Configuración de {self._config['nombre_tienda']}:")
        for k, v in self._config.items():
            print(f"     {k:<22}: {v}")

    # ── Helpers de negocio ────────────────────────────────
    def tipo_activo(self, tipo: str) -> bool:
        return tipo.upper() in self._config["tipos_activos"]

    def pasarela_activa(self, pasarela: str) -> bool:
        return pasarela.upper() in self._config["pasarelas_activas"]

    def generar_id_pedido(self) -> str:
        prefijo = self._config["prefijo_pedido"]
        id_pedido = f"{prefijo}-{self._correlativo_pedido:04d}"
        self._correlativo_pedido += 1
        return id_pedido

    def calcular_igv(self, subtotal: float) -> float:
        return round(subtotal * self._config["igv"], 2)
