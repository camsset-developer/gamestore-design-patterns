"""
CAPA: Infrastructure / Adapters
=================================
PATRÓN: ADAPTER
================
Cada pasarela de pago real tiene su propia API incompatible.
Los Adapters traducen esas APIs al contrato IPasarelaPago
que espera el resto de la aplicación.

APIs externas simuladas (Adaptees):
  PayPalSDK      → SDK de PayPal, trabaja en USD con métodos en inglés
  CulqiClient    → Cliente Culqi, trabaja en céntimos de soles
  YapeDirectAPI  → API de Yape, usa número de teléfono y PIN

Adapters:
  AdapterPayPal  → PayPalSDK   → IPasarelaPago
  AdapterCulqi   → CulqiClient → IPasarelaPago
  AdapterYape    → YapeAPI     → IPasarelaPago
"""

import random
import string
from domain.interfaces.interfaces import IPasarelaPago
from domain.model.modelos import Pedido


# ════════════════════════════════════════════════════
# ADAPTEES — APIs externas con sus propios formatos
# ════════════════════════════════════════════════════

class PayPalSDK:
    """
    SDK oficial de PayPal (simulado).
    - Trabaja exclusivamente en USD
    - Métodos y respuestas en inglés
    - Retorna objetos con estructura propia
    """

    def create_order(self, amount_usd: float, description: str) -> dict:
        order_id = "PP-" + ''.join(random.choices(string.digits, k=10))
        print(f"     [PayPal SDK] create_order: ${amount_usd:.2f} USD | {description}")
        return {
            "order_id":   order_id,
            "status":     "CREATED",
            "amount":     amount_usd,
            "currency":   "USD",
        }

    def capture_order(self, order_id: str) -> dict:
        print(f"     [PayPal SDK] capture_order: {order_id}")
        return {
            "capture_id": "CAP-" + order_id,
            "status":     "COMPLETED",
            "order_id":   order_id,
        }

    def get_order_details(self, order_id: str) -> dict:
        return {"order_id": order_id, "status": "COMPLETED", "provider": "PayPal"}


class CulqiClient:
    """
    Cliente oficial de Culqi (simulado).
    - Trabaja en CÉNTIMOS de soles (S/ 10.50 → 1050)
    - Retorna respuestas con estructura propia en español
    - Usa 'cargo_id' como identificador
    """

    def crear_cargo(self, monto_centimos: int, concepto: str, email: str) -> dict:
        cargo_id = "ch_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        print(f"     [Culqi Client] crear_cargo: S/{monto_centimos/100:.2f} | {concepto}")
        return {
            "cargo_id":   cargo_id,
            "estado":     "exitoso",
            "monto":      monto_centimos,
            "concepto":   concepto,
            "email":      email,
        }

    def consultar_cargo(self, cargo_id: str) -> dict:
        return {
            "cargo_id": cargo_id,
            "estado":   "exitoso",
            "proveedor": "Culqi",
        }


class YapeDirectAPI:
    """
    API directa de Yape (simulado).
    - Trabaja con número de teléfono peruano
    - Monto en soles (float)
    - Retorna código de operación numérico
    """

    def iniciar_pago(self, numero: str, monto: float, concepto: str) -> dict:
        codigo_op = random.randint(100000, 999999)
        print(f"     [Yape API] iniciar_pago: +51{numero} | S/{monto:.2f} | {concepto}")
        return {
            "codigo_operacion": codigo_op,
            "numero":           numero,
            "monto":            monto,
            "aprobado":         True,
        }

    def consultar_operacion(self, codigo_op: str) -> dict:
        return {
            "codigo_operacion": codigo_op,
            "aprobado":         True,
            "proveedor":        "Yape",
        }


# ════════════════════════════════════════════════════
# ADAPTERS — Traducen las APIs al contrato IPasarelaPago
# ════════════════════════════════════════════════════

class AdapterPayPal(IPasarelaPago):
    """
    Adapta el PayPalSDK → IPasarelaPago.

    Traducciones realizadas:
    - Monto: PEN → USD (÷ 3.75)
    - Métodos: cobrar() → create_order() + capture_order()
    - Respuesta: dict PayPal → dict estándar {exitoso, id_transaccion, mensaje}
    """

    TIPO_DE_CAMBIO = 3.75

    def __init__(self):
        self._sdk = PayPalSDK()

    def cobrar(self, pedido: Pedido, moneda: str) -> dict:
        print(f"\n  🔌 [ADAPTER PayPal] Traduciendo pedido {pedido.id} para SDK de PayPal...")

        # Traducción: PEN → USD
        monto_usd = round(pedido.total / self.TIPO_DE_CAMBIO, 2)
        descripcion = f"GameStore - Pedido {pedido.id}"

        # Llamadas al SDK externo con su propia API
        orden = self._sdk.create_order(monto_usd, descripcion)
        captura = self._sdk.capture_order(orden["order_id"])

        # Traducción: respuesta PayPal → formato estándar
        return {
            "exitoso":        captura["status"] == "COMPLETED",
            "id_transaccion": captura["capture_id"],
            "monto_cobrado":  pedido.total,
            "moneda":         "PEN",
            "mensaje":        f"Pago PayPal aprobado (${monto_usd} USD ≈ S/{pedido.total:.2f})",
        }

    def verificar(self, id_transaccion: str) -> dict:
        detalle = self._sdk.get_order_details(id_transaccion)
        return {
            "id_transaccion": id_transaccion,
            "estado":         "APROBADO" if detalle["status"] == "COMPLETED" else "PENDIENTE",
            "proveedor":      "PayPal",
        }

    def nombre(self) -> str:
        return "PayPal"


class AdapterCulqi(IPasarelaPago):
    """
    Adapta el CulqiClient → IPasarelaPago.

    Traducciones realizadas:
    - Monto: soles (float) → céntimos (int) (× 100)
    - Métodos: cobrar() → crear_cargo()
    - Respuesta: dict Culqi → dict estándar
    """

    def __init__(self):
        self._client = CulqiClient()

    def cobrar(self, pedido: Pedido, moneda: str) -> dict:
        print(f"\n  🔌 [ADAPTER Culqi] Traduciendo pedido {pedido.id} para Culqi...")

        # Traducción: soles → céntimos
        monto_centimos = int(pedido.total * 100)
        email_cliente = f"{pedido.cliente.lower().replace(' ', '.')}@email.com"

        # Llamada al cliente Culqi con su propia API
        cargo = self._client.crear_cargo(
            monto_centimos,
            f"Pedido {pedido.id} - GameStore",
            email_cliente,
        )

        # Traducción: respuesta Culqi → formato estándar
        return {
            "exitoso":        cargo["estado"] == "exitoso",
            "id_transaccion": cargo["cargo_id"],
            "monto_cobrado":  pedido.total,
            "moneda":         "PEN",
            "mensaje":        f"Pago Culqi aprobado — S/{pedido.total:.2f}",
        }

    def verificar(self, id_transaccion: str) -> dict:
        consulta = self._client.consultar_cargo(id_transaccion)
        return {
            "id_transaccion": id_transaccion,
            "estado":         "APROBADO" if consulta["estado"] == "exitoso" else "FALLIDO",
            "proveedor":      "Culqi",
        }

    def nombre(self) -> str:
        return "Culqi"


class AdapterYape(IPasarelaPago):
    """
    Adapta la YapeDirectAPI → IPasarelaPago.

    Traducciones realizadas:
    - cobrar() requiere número de teléfono → lo extrae del nombre del cliente
    - Respuesta: usa 'codigo_operacion' numérico → id_transaccion string
    - 'aprobado: True' → 'exitoso: True'
    """

    def __init__(self):
        self._api = YapeDirectAPI()

    def cobrar(self, pedido: Pedido, moneda: str) -> dict:
        print(f"\n  🔌 [ADAPTER Yape] Traduciendo pedido {pedido.id} para Yape API...")

        # Yape necesita número de teléfono: simulamos uno basado en el cliente
        numero_simulado = str(abs(hash(pedido.cliente)) % 900000000 + 900000000)[:9]

        # Llamada a la API de Yape con su propia estructura
        resultado = self._api.iniciar_pago(
            numero_simulado,
            pedido.total,
            f"Pedido {pedido.id}",
        )

        # Traducción: respuesta Yape → formato estándar
        return {
            "exitoso":        resultado["aprobado"],
            "id_transaccion": f"YAPE-{resultado['codigo_operacion']}",
            "monto_cobrado":  pedido.total,
            "moneda":         "PEN",
            "mensaje":        f"Yape aprobado — Código op: {resultado['codigo_operacion']}",
        }

    def verificar(self, id_transaccion: str) -> dict:
        codigo = id_transaccion.replace("YAPE-", "")
        consulta = self._api.consultar_operacion(codigo)
        return {
            "id_transaccion": id_transaccion,
            "estado":         "APROBADO" if consulta["aprobado"] else "FALLIDO",
            "proveedor":      "Yape",
        }

    def nombre(self) -> str:
        return "Yape"


# ── Registro de pasarelas disponibles ────────────────
PASARELAS = {
    "PAYPAL": AdapterPayPal,
    "CULQI":  AdapterCulqi,
    "YAPE":   AdapterYape,
}


def obtener_pasarela(nombre: str) -> IPasarelaPago:
    """Retorna la pasarela de pago solicitada."""
    key = nombre.upper()
    if key not in PASARELAS:
        disponibles = ", ".join(PASARELAS.keys())
        raise ValueError(f"Pasarela '{nombre}' no disponible. Opciones: {disponibles}")
    print(f"  🔌 [ADAPTER] Seleccionando pasarela: {key} → {PASARELAS[key].__name__}")
    return PASARELAS[key]()
