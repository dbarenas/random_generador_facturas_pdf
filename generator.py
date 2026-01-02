# -*- coding: utf-8 -*-
"""
Generador de 200 facturas de compra (España) en PDF.
- Español
- IVA España (21% / 10% / 4% según tipo de producto)
- 1 folio (A4) por factura -> 200 páginas en un único PDF
- Formato variado pero estructurado (varios layouts; ~45% variación visual)

Requisitos:
  pip install reportlab
Ejecución:
  python generar_facturas.py
Salida:
  facturas_compras_200.pdf
"""

import random
import math
from datetime import date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

W, H = A4

# -----------------------------
# Datos sintéticos (España)
# -----------------------------
PROVINCIAS = [
    ("Madrid", "Madrid"), ("Barcelona", "Barcelona"), ("Valencia", "Valencia"),
    ("Sevilla", "Sevilla"), ("Zaragoza", "Zaragoza"), ("Málaga", "Málaga"),
    ("Murcia", "Murcia"), ("Palma", "Illes Balears"), ("Bilbao", "Bizkaia"),
    ("Alicante", "Alicante"), ("Córdoba", "Córdoba"), ("Valladolid", "Valladolid"),
]

CALLES = [
    "C/ Mayor", "Av. de la Constitución", "C/ Gran Vía", "C/ Alcalá",
    "C/ Serrano", "C/ Aragón", "C/ Colón", "C/ del Sol", "C/ del Mar",
    "Pº de la Castellana", "C/ Sant Jaume", "C/ de la Paz"
]

EMPRESAS = [
    "Suministros Iberia S.L.", "Distribuciones Levante S.A.", "Servicios Atlas S.L.",
    "Comercial Norte S.L.", "Papelería Central S.A.", "Tecnología & Datos S.L.",
    "Almacenes Río Ebro S.L.", "Limpiezas Brisa S.L.", "Herramientas Orión S.A.",
    "OfiPlus S.L.", "Repuestos Mediterráneo S.L.", "HostelPro S.L."
]

CLIENTES = [
    "Construcciones Sierra S.L.", "Clínica San Gabriel S.L.", "Talleres Rápidos S.L.",
    "Gestión Integral Aragón S.L.", "Restauración La Plaza S.L.", "Consultoría Delta S.L.",
    "Innovación y Sistemas S.L.", "Logística Camino S.A.", "Farmacia Alameda C.B.",
    "Colegio Nuevo Horizonte", "Inmobiliaria Costa S.L.", "Eventos Luna S.L."
]

CATEGORIAS = [
    # (nombre, iva)
    ("Material de oficina", 0.21),
    ("Equipos informáticos", 0.21),
    ("Servicios profesionales", 0.21),
    ("Limpieza e higiene", 0.21),
    ("Hostelería (consumiciones)", 0.10),
    ("Alimentos básicos", 0.04),
    ("Repuestos y ferretería", 0.21),
    ("Transporte", 0.10),
]

PRODUCTOS = {
    "Material de oficina": [
        ("Papel A4 80g (caja)", 18.50),
        ("Bolígrafos (pack 10)", 6.40),
        ("Carpetas (pack 5)", 9.90),
        ("Tóner impresora", 54.00),
        ("Post-its (pack)", 3.20),
    ],
    "Equipos informáticos": [
        ("Teclado inalámbrico", 24.90),
        ("Ratón óptico", 12.50),
        ("Monitor 24\"", 129.00),
        ("Dock USB-C", 59.00),
        ("Disco SSD 1TB", 89.00),
    ],
    "Servicios profesionales": [
        ("Soporte IT (hora)", 45.00),
        ("Mantenimiento (mensual)", 180.00),
        ("Consultoría (hora)", 70.00),
        ("Instalación software", 120.00),
        ("Auditoría básica", 260.00),
    ],
    "Limpieza e higiene": [
        ("Gel hidroalcohólico (1L)", 5.90),
        ("Detergente industrial (5L)", 14.80),
        ("Papel higiénico (pack)", 8.60),
        ("Guantes nitrilo (caja)", 7.20),
        ("Bayetas microfibra (pack)", 4.40),
    ],
    "Hostelería (consumiciones)": [
        ("Café (servicio)", 1.40),
        ("Menú del día", 12.00),
        ("Agua (botella)", 1.10),
        ("Desayuno (servicio)", 4.50),
        ("Catering básico", 220.00),
    ],
    "Alimentos básicos": [
        ("Leche (caja 12)", 10.80),
        ("Pan (lote)", 6.20),
        ("Arroz (saco 5kg)", 7.90),
        ("Huevos (bandeja)", 4.10),
        ("Fruta variada (caja)", 16.50),
    ],
    "Repuestos y ferretería": [
        ("Tornillería (kit)", 8.30),
        ("Brocas (set)", 14.20),
        ("Lubricante (spray)", 5.70),
        ("Guía metálica", 11.90),
        ("Rodamiento", 9.40),
    ],
    "Transporte": [
        ("Servicio de mensajería", 8.50),
        ("Transporte palet", 42.00),
        ("Entrega urgente", 15.00),
        ("Ruta local", 28.00),
        ("Gestión logística", 75.00),
    ],
}

METODOS_PAGO = ["Transferencia", "Tarjeta", "Domiciliación", "Efectivo", "Pago a 30 días"]
BANCOS = ["Banco Santander", "BBVA", "CaixaBank", "Banco Sabadell", "Unicaja"]


def rand_nif():
    # NIF/CIF sintético (no real)
    letras = "ABCDEFGHJKLMNPQRSUVW"
    return f"{random.choice(letras)}{random.randint(10000000, 99999999)}"


def rand_cp():
    return f"{random.randint(1, 52):02d}{random.randint(0, 999):03d}"


def money(x):
    # 1.234,56 (formato ES)
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def split_lines(text, max_chars=64):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# -----------------------------
# Cálculo de líneas y totales
# -----------------------------
def generar_lineas():
    # 2 a 8 líneas
    n = random.randint(2, 8)
    lineas = []
    for _ in range(n):
        cat, iva = random.choice(CATEGORIAS)
        prod, base = random.choice(PRODUCTOS[cat])
        qty = random.randint(1, 8)
        # precios con variación
        unit = base * random.uniform(0.90, 1.15)
        # pequeños redondeos realistas
        unit = round(unit * 100) / 100.0
        lineas.append({
            "categoria": cat,
            "descripcion": prod,
            "cantidad": qty,
            "precio_unit": unit,
            "iva": iva,
        })
    return lineas


def calcular_totales(lineas):
    # Agrupar por tipo de IVA
    bases = {}
    cuotas = {}
    for l in lineas:
        base = l["cantidad"] * l["precio_unit"]
        iva = l["iva"]
        bases[iva] = bases.get(iva, 0.0) + base
    for iva, base in bases.items():
        cuotas[iva] = base * iva
    subtotal = sum(bases.values())
    total_iva = sum(cuotas.values())
    total = subtotal + total_iva
    return bases, cuotas, subtotal, total_iva, total


# -----------------------------
# Dibujos / estilos (layouts)
# -----------------------------
def draw_header_common(c, factura):
    # barra superior suave + título
    c.setFillColor(colors.whitesmoke)
    c.rect(15*mm, H-25*mm, W-30*mm, 12*mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18*mm, H-21*mm, "FACTURA (COMPRA)")
    c.setFont("Helvetica", 9)
    c.drawRightString(W-18*mm, H-20*mm, f"Nº {factura['numero']}  |  Fecha: {factura['fecha']}")


def draw_party_box(c, x, y, w, h, title, nombre, nif, direccion, cp, ciudad, provincia):
    c.setStrokeColor(colors.black)
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x+3*mm, y+h-5*mm, title)
    c.setFont("Helvetica", 8.5)
    lines = [
        nombre,
        f"NIF/CIF: {nif}",
        direccion,
        f"{cp} {ciudad} ({provincia})",
    ]
    yy = y+h-10*mm
    for ln in lines:
        c.drawString(x+3*mm, yy, ln)
        yy -= 4.2*mm


def draw_table_header(c, x, y, widths, variant=0):
    # widths: [desc, qty, unit, iva, total]
    labels = ["Descripción", "Cant.", "P. unit.", "IVA", "Importe"]
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(colors.lightgrey if variant in (0, 2) else colors.whitesmoke)
    c.rect(x, y, sum(widths), 7*mm, fill=1, stroke=1)
    c.setFillColor(colors.black)

    cx = x
    for i, (lab, w) in enumerate(zip(labels, widths)):
        if i == 0:
            c.drawString(cx+2*mm, y+2.2*mm, lab)
        else:
            c.drawRightString(cx+w-2*mm, y+2.2*mm, lab)
        cx += w


def draw_table_rows(c, x, y, widths, lineas, row_h=7*mm, zebra=True):
    c.setFont("Helvetica", 8.3)
    yy = y - row_h
    for idx, l in enumerate(lineas):
        if zebra and idx % 2 == 0:
            c.setFillColor(colors.whitesmoke)
            c.rect(x, yy, sum(widths), row_h, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.rect(x, yy, sum(widths), row_h, fill=0, stroke=1)

        desc = l["descripcion"]
        qty = l["cantidad"]
        unit = l["precio_unit"]
        iva = l["iva"]
        importe = qty * unit

        cx = x
        # Desc
        c.drawString(cx+2*mm, yy+2.0*mm, desc[:70])
        cx += widths[0]
        # Cant
        c.drawRightString(cx+widths[1]-2*mm, yy+2.0*mm, str(qty))
        cx += widths[1]
        # Unit
        c.drawRightString(cx+widths[2]-2*mm, yy+2.0*mm, f"{money(unit)} €")
        cx += widths[2]
        # IVA
        c.drawRightString(cx+widths[3]-2*mm, yy+2.0*mm, f"{int(iva*100)}%")
        cx += widths[3]
        # Total
        c.drawRightString(cx+widths[4]-2*mm, yy+2.0*mm, f"{money(importe)} €")

        yy -= row_h
    return yy


def draw_totals_box(c, x, y, w, bases, cuotas, subtotal, total_iva, total, variant=0):
    c.setStrokeColor(colors.black)
    if variant == 3:
        c.setFillColor(colors.whitesmoke)
        c.roundRect(x, y, w, 38*mm, 4*mm, fill=1, stroke=1)
    else:
        c.rect(x, y, w, 38*mm, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(x+3*mm, y+33*mm, "Resumen IVA")
    c.setFont("Helvetica", 8.5)
    yy = y+27*mm
    for iva in sorted(bases.keys(), reverse=True):
        c.drawString(x+3*mm, yy, f"Base {int(iva*100)}%:")
        c.drawRightString(x+w-3*mm, yy, f"{money(bases[iva])} €")
        yy -= 4.3*mm
        c.drawString(x+3*mm, yy, f"Cuota {int(iva*100)}%:")
        c.drawRightString(x+w-3*mm, yy, f"{money(cuotas[iva])} €")
        yy -= 5.2*mm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(x+3*mm, y+6.5*mm, "TOTAL FACTURA:")
    c.drawRightString(x+w-3*mm, y+6.5*mm, f"{money(total)} €")


def draw_footer(c, factura, variant=0):
    c.setFont("Helvetica", 8)
    note = factura["nota_pie"]
    lines = split_lines(note, max_chars=110)
    y = 14*mm
    if variant in (1, 3):
        c.setStrokeColor(colors.grey)
        c.line(15*mm, y+10*mm, W-15*mm, y+10*mm)
    for i, ln in enumerate(lines[:3]):
        c.drawString(15*mm, y + (7 - i*3.8)*mm, ln)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawRightString(W-15*mm, 10*mm, "Documento generado automáticamente (datos sintéticos).")


# -----------------------------
# Layouts (variedad)
# -----------------------------
def layout_0(c, factura):
    # Clásico: encabezado + dos cajas + tabla + resumen derecha
    draw_header_common(c, factura)

    # Cajas proveedor / cliente
    x1, y1, w1, h1 = 15*mm, H-70*mm, (W-35*mm)/2, 34*mm
    x2, y2, w2, h2 = x1+w1+5*mm, y1, w1, h1

    p = factura["proveedor"]
    cl = factura["cliente"]
    draw_party_box(c, x1, y1, w1, h1, "Proveedor", **p)
    draw_party_box(c, x2, y2, w2, h2, "Cliente", **cl)

    # Tabla
    table_x = 15*mm
    table_y = H-80*mm
    widths = [90*mm, 15*mm, 25*mm, 15*mm, 25*mm]  # desc, qty, unit, iva, total
    draw_table_header(c, table_x, table_y, widths, variant=0)
    yy = draw_table_rows(c, table_x, table_y, widths, factura["lineas"], zebra=True)

    # Totales
    bases, cuotas, subtotal, total_iva, total = factura["totales"]
    draw_totals_box(c, W-15*mm-65*mm, yy-42*mm, 65*mm, bases, cuotas, subtotal, total_iva, total, variant=0)

    # Info pago
    c.setFont("Helvetica", 8.5)
    c.drawString(15*mm, yy-12*mm, f"Método de pago: {factura['pago']}")
    c.drawString(15*mm, yy-17*mm, f"Banco: {factura['banco']}  |  IBAN: {factura['iban']}")

    draw_footer(c, factura, variant=0)


def layout_1(c, factura):
    # Moderno: banda lateral + cajas apiladas + tabla más estrecha y totales abajo
    # Banda lateral
    c.setFillColor(colors.lightgrey)
    c.rect(0, 0, 14*mm, H, fill=1, stroke=0)

    # Título
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(18*mm, H-22*mm, "Factura de compra")
    c.setFont("Helvetica", 9)
    c.drawString(18*mm, H-28*mm, f"Nº {factura['numero']}   ·   Fecha: {factura['fecha']}")

    # Proveedor / Cliente apilados
    p = factura["proveedor"]
    cl = factura["cliente"]
    draw_party_box(c, 18*mm, H-75*mm, W-36*mm, 24*mm, "Proveedor", **p)
    draw_party_box(c, 18*mm, H-104*mm, W-36*mm, 24*mm, "Cliente", **cl)

    # Tabla
    table_x = 18*mm
    table_y = H-115*mm
    widths = [95*mm, 15*mm, 22*mm, 15*mm, 25*mm]
    draw_table_header(c, table_x, table_y, widths, variant=1)
    yy = draw_table_rows(c, table_x, table_y, widths, factura["lineas"], zebra=False)

    # Totales abajo (ancho completo)
    bases, cuotas, subtotal, total_iva, total = factura["totales"]
    draw_totals_box(c, 18*mm, 50*mm, W-36*mm, bases, cuotas, subtotal, total_iva, total, variant=1)

    # Pago
    c.setFont("Helvetica", 8.5)
    c.drawString(18*mm, 44*mm, f"Pago: {factura['pago']}  |  Vencimiento: {factura['vencimiento']}")
    c.drawString(18*mm, 39*mm, f"IBAN: {factura['iban']}  ({factura['banco']})")

    draw_footer(c, factura, variant=1)


def layout_2(c, factura):
    # Compacto: encabezado en caja, tabla centrada, resumen a la izquierda
    # Encabezado en caja
    c.setFillColor(colors.whitesmoke)
    c.rect(15*mm, H-35*mm, W-30*mm, 18*mm, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18*mm, H-24*mm, "FACTURA")
    c.setFont("Helvetica", 9)
    c.drawRightString(W-18*mm, H-24*mm, f"Nº {factura['numero']}  ·  Fecha: {factura['fecha']}")

    # Mini cajas proveedor/cliente
    p = factura["proveedor"]
    cl = factura["cliente"]
    draw_party_box(c, 15*mm, H-63*mm, (W-30*mm), 24*mm, "Proveedor", **p)
    draw_party_box(c, 15*mm, H-92*mm, (W-30*mm), 24*mm, "Cliente", **cl)

    # Tabla
    table_x = 15*mm
    table_y = H-103*mm
    widths = [92*mm, 16*mm, 24*mm, 15*mm, 26*mm]
    draw_table_header(c, table_x, table_y, widths, variant=2)
    yy = draw_table_rows(c, table_x, table_y, widths, factura["lineas"], zebra=True)

    # Resumen izquierda + pago derecha
    bases, cuotas, subtotal, total_iva, total = factura["totales"]
    draw_totals_box(c, 15*mm, yy-45*mm, 85*mm, bases, cuotas, subtotal, total_iva, total, variant=2)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(110*mm, yy-12*mm, "Datos de pago")
    c.setFont("Helvetica", 8.5)
    c.drawString(110*mm, yy-18*mm, f"Pago: {factura['pago']}")
    c.drawString(110*mm, yy-23*mm, f"Venc.: {factura['vencimiento']}")
    c.drawString(110*mm, yy-28*mm, f"Banco: {factura['banco']}")
    c.drawString(110*mm, yy-33*mm, f"IBAN: {factura['iban']}")

    draw_footer(c, factura, variant=2)


def layout_3(c, factura):
    # “Tarjeta”: cabecera simple, cajas redondeadas, tabla, totales redondeados
    c.setFont("Helvetica-Bold", 15)
    c.drawString(15*mm, H-20*mm, "Factura de compra")
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, H-26*mm, f"Nº {factura['numero']}  |  Fecha: {factura['fecha']}")

    # Cajas redondeadas
    p = factura["proveedor"]
    cl = factura["cliente"]

    def round_party(title, data, x, y, w, h):
        c.setFillColor(colors.whitesmoke)
        c.roundRect(x, y, w, h, 4*mm, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x+3*mm, y+h-5*mm, title)
        c.setFont("Helvetica", 8.5)
        lines = [
            data["nombre"],
            f"NIF/CIF: {data['nif']}",
            data["direccion"],
            f"{data['cp']} {data['ciudad']} ({data['provincia']})",
        ]
        yy = y+h-10*mm
        for ln in lines:
            c.drawString(x+3*mm, yy, ln)
            yy -= 4.2*mm

    x1, y1, w1, h1 = 15*mm, H-68*mm, (W-35*mm)/2, 36*mm
    x2, y2, w2, h2 = x1+w1+5*mm, y1, w1, h1
    round_party("Proveedor", p, x1, y1, w1, h1)
    round_party("Cliente", cl, x2, y2, w2, h2)

    # Tabla
    table_x = 15*mm
    table_y = H-80*mm
    widths = [88*mm, 16*mm, 26*mm, 15*mm, 28*mm]
    draw_table_header(c, table_x, table_y, widths, variant=3)
    yy = draw_table_rows(c, table_x, table_y, widths, factura["lineas"], zebra=False)

    # Totales redondeados
    bases, cuotas, subtotal, total_iva, total = factura["totales"]
    draw_totals_box(c, W-15*mm-70*mm, 40*mm, 70*mm, bases, cuotas, subtotal, total_iva, total, variant=3)

    # Nota/pago
    c.setFont("Helvetica", 8.5)
    c.drawString(15*mm, 46*mm, f"Pago: {factura['pago']}  |  Vencimiento: {factura['vencimiento']}")
    c.drawString(15*mm, 41*mm, f"{factura['banco']}  ·  IBAN: {factura['iban']}")

    draw_footer(c, factura, variant=3)


LAYOUTS = [layout_0, layout_1, layout_2, layout_3]
# Pesos para que haya variedad, pero no totalmente uniforme
LAYOUT_WEIGHTS = [0.30, 0.25, 0.25, 0.20]  # ~45% de variación percibida entre estilos


# -----------------------------
# Factura completa (objeto)
# -----------------------------
def generar_factura(i, start_date):
    prov_ciudad, prov_provincia = random.choice(PROVINCIAS)
    cli_ciudad, cli_provincia = random.choice(PROVINCIAS)

    proveedor = {
        "nombre": random.choice(EMPRESAS),
        "nif": rand_nif(),
        "direccion": f"{random.choice(CALLES)} {random.randint(1, 220)}",
        "cp": rand_cp(),
        "ciudad": prov_ciudad,
        "provincia": prov_provincia
    }
    cliente = {
        "nombre": random.choice(CLIENTES),
        "nif": rand_nif(),
        "direccion": f"{random.choice(CALLES)} {random.randint(1, 220)}",
        "cp": rand_cp(),
        "ciudad": cli_ciudad,
        "provincia": cli_provincia
    }

    # Fecha en ventana de ~90 días
    f = start_date + timedelta(days=random.randint(0, 90))
    fecha_str = f.strftime("%d/%m/%Y")

    lineas = generar_lineas()
    totales = calcular_totales(lineas)

    pago = random.choice(METODOS_PAGO)
    venc = f + timedelta(days=random.choice([0, 7, 15, 30, 45]))
    venc_str = venc.strftime("%d/%m/%Y")

    iban = f"ES{random.randint(10,99)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(10,99)}{random.randint(0,9999999999):010d}"
    banco = random.choice(BANCOS)

    notas = [
        "Gracias por su compra. Conserve esta factura como justificante.",
        "Pago según condiciones acordadas. En caso de devolución, conservar embalaje original.",
        "Esta factura se emite conforme a la normativa vigente. Importes en euros (€).",
        "Factura generada con datos sintéticos para pruebas y validaciones de sistemas.",
    ]

    return {
        "numero": f"F-{f.year}-{i:05d}",
        "fecha": fecha_str,
        "proveedor": proveedor,
        "cliente": cliente,
        "lineas": lineas,
        "totales": totales,
        "pago": pago,
        "vencimiento": venc_str,
        "iban": iban,
        "banco": banco,
        "nota_pie": random.choice(notas),
    }


# -----------------------------
# Generación PDF
# -----------------------------
def generar_pdf(path="facturas_compras_200.pdf", n=200, seed=7):
    random.seed(seed)
    c = canvas.Canvas(path, pagesize=A4)
    start_date = date(2025, 9, 1)

    for i in range(1, n+1):
        factura = generar_factura(i, start_date)

        layout = random.choices(LAYOUTS, weights=LAYOUT_WEIGHTS, k=1)[0]
        layout(c, factura)

        # 1 folio por factura
        c.showPage()

    c.save()
    print(f"OK -> {path} (páginas: {n})")


if __name__ == "__main__":
    generar_pdf()
