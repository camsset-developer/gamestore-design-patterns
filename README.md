# 🎮 GameStore Perú — Tienda de Videojuegos

Aplicación de consola en Python que implementa **3 patrones de diseño** dentro de una **arquitectura en capas**, simulando una tienda de videojuegos con catálogo, carrito, y múltiples métodos de pago.

---

## 🏗️ Arquitectura del sistema

```
gamestore/
│
├── domain/                            ← Capa de Dominio (reglas puras)
│   ├── model/
│   │   └── modelos.py                 → Entidades: Producto, Pedido, ItemPedido
│   └── interfaces/
│       └── interfaces.py              → Contratos: IProducto, IPasarelaPago
│
├── infrastructure/                    ← Capa de Infraestructura (detalles técnicos)
│   ├── config/
│   │   └── configuracion.py           → 🔵 PATRÓN SINGLETON
│   ├── factory/
│   │   └── producto_factory.py        → 🟡 PATRÓN FACTORY METHOD
│   └── adapters/
│       └── adapters_pago.py           → 🟠 PATRÓN ADAPTER
│
├── application/                       ← Capa de Aplicación (orquestación)
│   └── services/
│       └── tienda_service.py          → Une los 3 patrones en un flujo coherente
│
├── presentation/                      ← Capa de Presentación (UI)
│   └── menu.py                        → Menú interactivo en consola
│
└── main.py                            → Punto de entrada
```

### Flujo completo

```
Usuario (menú)
    │
    ▼
TiendaService
    ├── ConfiguracionTienda (SINGLETON)  → valida pasarela, genera ID de pedido
    │
    ├── ProductoFactory.crear() (FACTORY)
    │       ├── "FISICO"      → ProductoFisico     (valida stock, descuenta)
    │       ├── "DIGITAL"     → ProductoDigital    (genera clave de activación)
    │       ├── "DLC"         → ProductoDLC        (activa en biblioteca)
    │       └── "SUSCRIPCION" → ProductoSuscripcion (activa días de acceso)
    │
    └── obtener_pasarela() (ADAPTER)
            ├── "PAYPAL" → AdapterPayPal → PayPalSDK     (USD, inglés)
            ├── "CULQI"  → AdapterCulqi  → CulqiClient   (céntimos PEN)
            └── "YAPE"   → AdapterYape   → YapeDirectAPI (teléfono, código op)
```

---

## 🎯 Patrones de diseño

### 🔵 Singleton — `infrastructure/config/configuracion.py`

**Problema:** La tienda necesita una configuración global única (nombre, moneda, tipos activos, pasarelas). Si hubiera múltiples instancias, podría haber configuraciones contradictorias.

**Solución:** `ConfiguracionTienda` controla su propia creación en `__new__`. La segunda llamada devuelve exactamente la misma instancia.

```python
config1 = ConfiguracionTienda()  # ✅ Crea la instancia
config2 = ConfiguracionTienda()  # ♻️ Retorna la misma
config1 is config2  →  True
```

**¿Dónde actúa en la app?**
- Valida si una pasarela está activa antes de cobrar
- Genera el ID correlativo de cada pedido (`ORD-0001`, `ORD-0002`...)
- Calcula el IGV

---

### 🟡 Factory Method — `infrastructure/factory/producto_factory.py`

**Problema:** Cada tipo de producto tiene reglas distintas: los físicos tienen stock, los digitales generan claves, los DLC solo permiten 1 unidad. El servicio no debería conocer esas diferencias.

**Solución:** `ProductoFactory.crear(producto)` devuelve el manejador correcto según el tipo.

```python
ProductoFactory.crear(producto_fisico)      → ProductoFisico
ProductoFactory.crear(producto_digital)     → ProductoDigital
ProductoFactory.crear(producto_dlc)         → ProductoDLC
ProductoFactory.crear(producto_suscripcion) → ProductoSuscripcion
```

**¿Dónde actúa en la app?**
- Al agregar al carrito: valida según las reglas del tipo
- Al confirmar el pago: ejecuta la entrega correcta (descuenta stock, genera clave, activa suscripción)

---

### 🟠 Adapter — `infrastructure/adapters/adapters_pago.py`

**Problema:** Cada pasarela de pago tiene una API completamente diferente e incompatible:

| Pasarela | API propia | Formato |
|----------|-----------|---------|
| PayPal | `create_order()` + `capture_order()` | USD, inglés |
| Culqi | `crear_cargo()` | Céntimos de soles (int) |
| Yape | `iniciar_pago()` | Número teléfono + código operación |

El sistema solo conoce una interfaz: `IPasarelaPago.cobrar(pedido, moneda)`.

**Solución:** Tres adaptadores traducen cada API al contrato estándar:

```
Sistema → AdapterPayPal → PayPalSDK     (convierte PEN→USD, crea orden, captura)
Sistema → AdapterCulqi  → CulqiClient   (convierte soles→céntimos)
Sistema → AdapterYape   → YapeDirectAPI (extrae teléfono, traduce respuesta)
```

**¿Dónde actúa en la app?**
- Al finalizar la compra con cualquier método de pago

---

## 🚀 Instalación y ejecución

### Requisitos
- Python 3.10+
- Sin dependencias externas

### Clonar y ejecutar

```bash
python main.py
```

### Flujo de prueba recomendado

1. **[1] Ver catálogo** → observa los 4 tipos de producto
2. **[2] Agregar al carrito** → ingresa tu nombre, agrega `G001` (Digital), `G002` (Físico), `G006` (DLC), `G007` (Suscripción)
   - La consola muestra el **Factory** creando el manejador correcto para cada tipo
3. **[4] Finalizar compra** → elige PayPal, Culqi o Yape
   - La consola muestra el **Adapter** traduciendo para cada pasarela
   - El **Factory** ejecuta la entrega diferenciada por tipo
4. **[6] Configuración** → ve el **Singleton** en acción

---

## 📊 Resumen de patrones

| Patrón | Categoría | Problema | Clase |
|--------|-----------|----------|-------|
| Singleton | Creacional | Una sola config global | `ConfiguracionTienda` |
| Factory | Creacional | Crear el producto correcto sin acoplar | `ProductoFactory` |
| Adapter | Estructural | Unificar APIs de pago incompatibles | `AdapterPayPal`, `AdapterCulqi`, `AdapterYape` |

---

## 📚 Referencias

- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns*. Addison-Wesley.
- Refactoring.Guru. https://refactoring.guru/design-patterns

---

## 👩‍💻 Autor

Desarrollado para el curso de **Arquitectura de Software** — Módulo 2: Patrones de Diseño.
