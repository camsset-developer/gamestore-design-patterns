"""
GameStore — Punto de entrada
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.config.configuracion import ConfiguracionTienda
from application.services.tienda_service import TiendaService
from presentation.menu import menu_principal


def main():
    print("\n" + "═" * 58)
    print("  🎮 Iniciando GameStore Perú")
    print("═" * 58)

    # SINGLETON: primera y única instancia
    config  = ConfiguracionTienda()
    config2 = ConfiguracionTienda()   # demuestra que es la misma
    print(f"\n  🔁 Singleton verificado: config is config2 → {config is config2}")
    print(f"  🏪 Tienda  : {config.obtener('nombre_tienda')}")
    print(f"  💰 Moneda  : {config.obtener('moneda')}")
    print(f"  📦 Tipos   : {config.obtener('tipos_activos')}")
    print(f"  💳 Pagos   : {config.obtener('pasarelas_activas')}")

    svc = TiendaService()
    menu_principal(svc, config)


if __name__ == "__main__":
    main()
