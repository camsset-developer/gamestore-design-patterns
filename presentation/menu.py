"""
CAPA: Presentation
====================
Menú interactivo en consola. Solo habla con TiendaService.
"""
import os
from application.services.tienda_service import TiendaService
from infrastructure.config.configuracion import ConfiguracionTienda


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def sep(titulo=""):
    print("\n" + "═" * 58)
    if titulo:
        print(f"  {titulo}")
        print("═" * 58)


def enter():
    input("\n  Presiona ENTER para continuar...")


# ── Menú principal ───────────────────────────────────────

def menu_principal(svc: TiendaService, config: ConfiguracionTienda):
    while True:
        cls()
        sep(f"🎮 {config.obtener('nombre_tienda')} — Menú Principal")
        print(f"""
  [1] 📋 Ver catálogo
  [2] 🛒 Agregar al carrito
  [3] 🧾 Ver carrito
  [4] 💳 Finalizar compra
  [5] 📦 Historial de pedidos
  [6] ⚙️  Configuración de la tienda
  [0] 🚪 Salir
        """)

        if svc._cliente_actual:
            print(f"  👤 Cliente: {svc._cliente_actual}  |  "
                  f"Carrito: {len(svc.ver_carrito())} item(s)  |  "
                  f"Total: S/ {svc.total_carrito():.2f}")

        op = input("\n  Opción: ").strip()

        if op == "1":   menu_catalogo(svc)
        elif op == "2": menu_agregar(svc)
        elif op == "3": menu_carrito(svc)
        elif op == "4": menu_checkout(svc)
        elif op == "5": menu_historial(svc)
        elif op == "6":
            sep("⚙️  Configuración")
            config.mostrar()
            enter()
        elif op == "0":
            print("\n  👋 ¡Gracias por visitar GameStore!\n")
            break
        else:
            print("  ❌ Opción inválida.")
            enter()


# ── Submenús ─────────────────────────────────────────────

def menu_catalogo(svc: TiendaService):
    sep("📋 Catálogo de Juegos")
    print("  Filtrar por: [1] Todos  [2] Físico  [3] Digital  [4] DLC  [5] Suscripción")
    f = input("  Filtro: ").strip()
    filtros = {"2": "FISICO", "3": "DIGITAL", "4": "DLC", "5": "SUSCRIPCION"}
    filtro = filtros.get(f, "")

    productos = svc.listar_catalogo(filtro)
    print(f"\n  {'ID':<6} {'Nombre':<35} {'Plataforma':<18} {'Tipo':<12} {'Precio':>8}")
    print(f"  {'─'*82}")
    for p in productos:
        stock_txt = f"(stock: {p.stock})" if p.tipo == "FISICO" else ""
        print(f"  {p.id:<6} {p.nombre:<35} {p.plataforma:<18} {p.tipo:<12} "
              f"S/{p.precio:>7.2f} {stock_txt}")
    enter()


def menu_agregar(svc: TiendaService):
    sep("🛒 Agregar al Carrito")

    if not svc._cliente_actual:
        nombre = input("  Primero ingresa tu nombre: ").strip()
        if not nombre:
            print("  ❌ Nombre requerido.")
            enter()
            return
        svc.set_cliente(nombre)
        print(f"  ✅ Bienvenido, {nombre}!")

    id_p = input("\n  ID del producto (ej: G001): ").strip().upper()
    if not id_p:
        return

    producto = svc.buscar_producto(id_p)
    if not producto:
        print(f"  ❌ Producto '{id_p}' no encontrado.")
        enter()
        return

    print(f"  Producto: {producto}")
    try:
        cant = int(input("  Cantidad: ").strip() or "1")
    except ValueError:
        cant = 1

    ok, msg = svc.agregar_al_carrito(id_p, cant)
    print(f"\n  {'✅' if ok else '❌'} {msg}")
    enter()


def menu_carrito(svc: TiendaService):
    sep("🧾 Tu Carrito")
    items = svc.ver_carrito()

    if not items:
        print("  El carrito está vacío.")
        enter()
        return

    print(f"\n  {'Producto':<35} {'Cant':>5} {'P.Unit':>8} {'Subtotal':>10}")
    print(f"  {'─'*62}")
    for item in items:
        print(f"  {item.producto.nombre:<35} {item.cantidad:>5} "
              f"S/{item.precio_unitario:>7.2f} S/{item.subtotal:>9.2f}")
    print(f"  {'─'*62}")

    igv = ConfiguracionTienda().calcular_igv(svc.total_carrito())
    print(f"  {'Subtotal':>50} S/{svc.total_carrito():>9.2f}")
    print(f"  {'IGV (18%)':>50} S/{igv:>9.2f}")
    print(f"  {'TOTAL':>50} S/{svc.total_carrito():>9.2f}")

    print("\n  [1] Continuar comprando  [2] Vaciar carrito  [ENTER] Volver")
    op = input("  Opción: ").strip()
    if op == "2":
        svc.vaciar_carrito()
        print("  🗑️  Carrito vaciado.")
        enter()


def menu_checkout(svc: TiendaService):
    sep("💳 Finalizar Compra")

    if not svc._cliente_actual or not svc.ver_carrito():
        print("  ⚠️  Agrega productos al carrito primero.")
        enter()
        return

    pedido = svc.crear_pedido()
    pedido.mostrar()

    print(f"\n  Método de pago:")
    print(f"    [1] PayPal    [2] Culqi    [3] Yape")
    metodos = {"1": "PAYPAL", "2": "CULQI", "3": "YAPE"}
    op = input("  Elige método: ").strip()
    metodo = metodos.get(op)

    if not metodo:
        print("  ❌ Método inválido.")
        enter()
        return

    print(f"\n  Procesando pago con {metodo}...")
    print("  " + "─" * 54)
    ok, msg = svc.procesar_pago(pedido, metodo)

    if ok:
        print(f"\n  ✅ {msg}")
        pedido.mostrar()
    else:
        print(f"\n  ❌ {msg}")

    enter()


def menu_historial(svc: TiendaService):
    sep("📦 Historial de Pedidos")
    pedidos = svc.historial_pedidos()

    if not pedidos:
        print("  No hay pedidos registrados aún.")
    else:
        for p in pedidos:
            icono = "🟢" if p.estado == "PAGADO" else "🔴"
            print(f"\n  {icono} Pedido {p.id} | {p.cliente} | "
                  f"S/{p.total:.2f} | {p.metodo_pago}")
            for item in p.items:
                print(f"     → {item.cantidad}x {item.producto.nombre}")

    enter()
