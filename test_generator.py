import os
import pytest
from generator import calcular_totales, generar_pdf, generar_factura
from datetime import date

# Pruebas Unitarias para calcular_totales
def test_calcular_totales_simple():
    """Prueba el cálculo de totales con una línea de factura simple."""
    lineas = [
        {"cantidad": 2, "precio_unit": 10.0, "iva": 0.21}
    ]
    bases, cuotas, subtotal, total_iva, total = calcular_totales(lineas)

    assert subtotal == pytest.approx(20.0)
    assert total_iva == pytest.approx(4.2)
    assert total == pytest.approx(24.2)
    assert bases[0.21] == pytest.approx(20.0)
    assert cuotas[0.21] == pytest.approx(4.2)

def test_calcular_totales_multi_iva():
    """Prueba el cálculo de totales con múltiples tipos de IVA."""
    lineas = [
        {"cantidad": 2, "precio_unit": 10.0, "iva": 0.21}, # Base: 20, IVA: 4.2
        {"cantidad": 1, "precio_unit": 100.0, "iva": 0.10}, # Base: 100, IVA: 10
        {"cantidad": 3, "precio_unit": 5.0, "iva": 0.04}   # Base: 15, IVA: 0.6
    ]
    bases, cuotas, subtotal, total_iva, total = calcular_totales(lineas)

    assert subtotal == pytest.approx(135.0)
    assert total_iva == pytest.approx(14.8)
    assert total == pytest.approx(149.8)

    assert len(bases) == 3
    assert bases[0.21] == pytest.approx(20.0)
    assert bases[0.10] == pytest.approx(100.0)
    assert bases[0.04] == pytest.approx(15.0)

    assert len(cuotas) == 3
    assert cuotas[0.21] == pytest.approx(4.2)
    assert cuotas[0.10] == pytest.approx(10.0)
    assert cuotas[0.04] == pytest.approx(0.6)

def test_calcular_totales_sin_lineas():
    """Prueba el cálculo de totales con una lista de líneas vacía."""
    lineas = []
    bases, cuotas, subtotal, total_iva, total = calcular_totales(lineas)

    assert subtotal == 0.0
    assert total_iva == 0.0
    assert total == 0.0
    assert not bases
    assert not cuotas

# Pruebas de Integración para la generación de PDF
@pytest.fixture
def pdf_cleanup():
    """Fixture para limpiar los archivos PDF generados después de las pruebas."""
    test_files = []
    yield test_files
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)

def test_generar_pdf_una_factura(pdf_cleanup):
    """Prueba que se genera un PDF con una sola factura."""
    test_pdf_path = "test_factura_unica.pdf"
    pdf_cleanup.append(test_pdf_path)

    generar_pdf(path=test_pdf_path, n=1, seed=42)

    assert os.path.exists(test_pdf_path), f"El archivo PDF no fue creado en {test_pdf_path}"
    # Opcional: verificar que el archivo no está vacío
    assert os.path.getsize(test_pdf_path) > 0, "El archivo PDF está vacío"

def test_generar_factura_estructura():
    """Prueba que la función generar_factura devuelve la estructura de datos esperada."""
    start_date = date(2023, 1, 1)
    factura = generar_factura(1, start_date)

    # Verificar claves principales
    expected_keys = [
        "numero", "fecha", "proveedor", "cliente", "lineas",
        "totales", "pago", "vencimiento", "iban", "banco", "nota_pie"
    ]
    for key in expected_keys:
        assert key in factura, f"La clave '{key}' falta en la factura generada"

    # Verificar sub-estructuras
    assert "nombre" in factura["proveedor"]
    assert "nombre" in factura["cliente"]
    assert isinstance(factura["lineas"], list)
    assert len(factura["lineas"]) > 0
    assert "descripcion" in factura["lineas"][0]
    assert isinstance(factura["totales"], tuple)
    assert len(factura["totales"]) == 5
