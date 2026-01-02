# Generador de Facturas en PDF

Este script de Python genera facturas de compra (España) en formato PDF. Es útil para crear datos de prueba o para demostraciones de sistemas que procesan facturas.

## Características

- **Generación de Múltiples Facturas**: Puede generar cualquier número de facturas en un solo comando.
- **Datos Sintéticos Realistas**: Utiliza datos sintéticos para nombres de empresas, clientes, productos y direcciones en España.
- **Cálculo de IVA (España)**: Aplica los tipos de IVA españoles correctos (21%, 10%, 4%) según la categoría del producto.
- **Múltiples Diseños**: Incluye varios diseños de factura para proporcionar variedad visual.
- **Salida en PDF**: Genera las facturas en formato PDF, ya sea en un único archivo o en archivos individuales.

## Requisitos

- Python 3.x
- Biblioteca `reportlab`

Para instalar la dependencia, ejecuta:
```bash
pip install reportlab
```

## Uso

Para generar un único archivo PDF con 200 facturas:
```bash
python generator.py
```
Esto creará un archivo llamado `facturas_compras_200.pdf`.

Para generar 10 facturas en archivos PDF separados:
```bash
python generator.py --individuales 10
```
Esto creará 10 archivos PDF, llamados `factura_1.pdf`, `factura_2.pdf`, etc.

## Explicación de Variables

A continuación se describen las principales variables y estructuras de datos utilizadas en `generator.py`:

- `PROVINCIAS`: Una lista de tuplas que contiene nombres de ciudades y sus provincias correspondientes en España.
- `CALLES`: Una lista de nombres de calles comunes.
- `EMPRESAS`: Una lista de nombres de empresas proveedoras.
- `CLIENTES`: Una lista de nombres de empresas clientes.
- `CATEGORIAS`: Una lista de tuplas que define las categorías de productos y el tipo de IVA aplicable a cada una.
- `PRODUCTOS`: Un diccionario que asigna productos (con su precio base) a cada categoría. Los precios pueden variar ligeramente en cada factura generada.
- `METODOS_PAGO`: Una lista de métodos de pago comunes.
- `BANCOS`: Una lista de los principales bancos de España.

### Estructura de una Factura (diccionario)

El script crea un diccionario para cada factura con la siguiente estructura:

- `numero`: (str) El número de factura (ej. "F-2025-00001").
- `fecha`: (str) La fecha de la factura en formato "dd/mm/aaaa".
- `proveedor`: (dict) Un diccionario con los datos del proveedor:
    - `nombre`, `nif`, `direccion`, `cp`, `ciudad`, `provincia`.
- `cliente`: (dict) Un diccionario con los datos del cliente, con la misma estructura que el proveedor.
- `lineas`: (list) Una lista de diccionarios, donde cada diccionario representa una línea de la factura:
    - `categoria`, `descripcion`, `cantidad`, `precio_unit`, `iva`.
- `totales`: (tuple) Una tupla que contiene:
    - `bases`: (dict) Un diccionario con las bases imponibles agrupadas por tipo de IVA.
    - `cuotas`: (dict) Un diccionario con las cuotas de IVA agrupadas por tipo de IVA.
    - `subtotal`: (float) El subtotal de la factura (suma de las bases).
    - `total_iva`: (float) El total de IVA de la factura (suma de las cuotas).
    - `total`: (float) El total de la factura.
- `pago`: (str) El método de pago.
- `vencimiento`: (str) La fecha de vencimiento de la factura.
- `iban`: (str) Un número IBAN sintético.
- `banco`: (str) El nombre del banco.
- `nota_pie`: (str) Una nota aleatoria para el pie de página de la factura.
