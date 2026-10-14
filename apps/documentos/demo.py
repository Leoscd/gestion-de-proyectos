"""Documentos de demostración. Pasan por los mismos servicios que una carga real
(huella, lectura de datos, versiones, aprobación y registro de actividad)."""

import io
from datetime import date, timedelta
from decimal import Decimal

from django.core.files.base import ContentFile

from apps.cuentas.models import Area

from . import services
from .models import Documento

A = Area.Codigo
T = Documento.Tipo


def _pdf(titulo, lineas, dibujo=False):
    """Un PDF mínimo de una página con texto (y un esquema de planta si dibujo=True)."""
    def esc(t):
        return t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    ops = [f"BT /F1 18 Tf 50 790 Td ({esc(titulo)}) Tj ET"]
    y = 765
    for linea in lineas:
        ops.append(f"BT /F1 10 Tf 50 {y} Td ({esc(linea)}) Tj ET")
        y -= 15
    if dibujo:
        ops += ["1 w 80 120 435 420 re S", "80 330 m 515 330 l S", "300 120 m 300 540 l S",
                "2 w 80 120 435 420 re S", "0.5 w 380 330 m 380 540 l S",
                "BT /F1 9 Tf 150 430 Td (ESTAR - COMEDOR) Tj ET", "BT /F1 9 Tf 360 220 Td (COCINA) Tj ET",
                "BT /F1 9 Tf 150 220 Td (DORMITORIO 1) Tj ET", "BT /F1 9 Tf 420 430 Td (BANO) Tj ET",
                "BT /F1 8 Tf 430 90 Td (Esc. 1:50) Tj ET"]
    contenido = "\n".join(ops).encode("latin-1")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> "
        b"/Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(contenido) + contenido + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    salida = b"%PDF-1.4\n"
    posiciones = []
    for i, objeto in enumerate(objetos, 1):
        posiciones.append(len(salida))
        salida += b"%d 0 obj\n" % i + objeto + b"\nendobj\n"
    xref = len(salida)
    salida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for p in posiciones:
        salida += b"%010d 00000 n \n" % p
    salida += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    return salida


def _xlsx(hojas):
    from openpyxl import Workbook

    libro = Workbook()
    libro.remove(libro.active)
    for nombre, filas in hojas.items():
        hoja = libro.create_sheet(nombre)
        for fila in filas:
            hoja.append(fila)
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def _foto():
    from PIL import Image, ImageDraw

    imagen = Image.new("RGB", (1200, 900), (150, 190, 225))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle([0, 560, 1200, 900], fill=(140, 120, 95))
    dibujo.rectangle([220, 330, 980, 600], fill=(170, 170, 165))       # losa y tabiques
    dibujo.rectangle([220, 300, 980, 335], fill=(120, 120, 118))       # borde de losa
    for x in range(250, 980, 120):
        dibujo.rectangle([x, 335, x + 22, 600], fill=(110, 110, 108))  # columnas
    exif = Image.Exif()
    exif[306] = "2026:09:29 10:15:00"
    salida = io.BytesIO()
    imagen.save(salida, "JPEG", quality=85, exif=exif)
    return salida.getvalue()


def cargar_documentos_demo(obra, personas):
    if obra.documentos.exists():
        return
    areas = {a.codigo: a for a in Area.objects.all()}
    desarrollo, tecnica = personas[A.DESARROLLO_PROYECTOS], personas[A.DIRECCION_TECNICA]
    jefe_obra, admin = personas[A.GESTION_OBRAS], personas[A.GESTION_ADMINISTRATIVA]
    gerencia = personas[A.GERENCIA]

    def archivo(nombre, contenido):
        return ContentFile(contenido, name=nombre)

    # Planos: A-101 con dos revisiones, aprobado y compartido; A-102 en revisión; E-201 en elaboración.
    a101, _ = services.crear_documento(
        desarrollo, archivo("A-101_Planta baja_RevA.pdf", _pdf("A-101 Planta baja - Rev A", ["Casa Pérez"], True)),
        obra=obra, tipo=T.PLANOS, area=areas[A.DESARROLLO_PROYECTOS], especialidad="arquitectura", escala="1:50",
        comentario="Primera emisión")
    services.agregar_version(
        a101, desarrollo,
        archivo("A-101_Planta baja_RevB.pdf", _pdf("A-101 Planta baja - Rev B", ["Cocina integrada"], True)),
        comentario="Se integró la cocina al estar a pedido del cliente", revision="B")
    services.pasar_a_revision(a101, desarrollo)
    services.aprobar_plano(a101, tecnica)
    services.cambiar_acceso(a101, jefe_obra, Documento.Acceso.CLIENTE)

    a102, _ = services.crear_documento(
        desarrollo, archivo("A-102_Planta alta_RevA.pdf", _pdf("A-102 Planta alta - Rev A", ["Casa Pérez"], True)),
        obra=obra, tipo=T.PLANOS, area=areas[A.DESARROLLO_PROYECTOS], especialidad="arquitectura", escala="1:50")
    services.pasar_a_revision(a102, desarrollo)

    services.crear_documento(
        desarrollo, archivo("E-201_Losa sobre planta baja.pdf", _pdf("E-201 Losa sobre planta baja", ["H-21"], True)),
        obra=obra, tipo=T.PLANOS, area=areas[A.DESARROLLO_PROYECTOS], especialidad="estructura", escala="1:50")

    # Planillas y presupuestos.
    services.crear_documento(
        desarrollo, archivo("Planilla de carpinterias.xlsx", _xlsx({"Carpinterías": [
            ["Código", "Tipo", "Ancho (m)", "Alto (m)", "Cantidad", "Material", "Apertura"],
            ["V1", "Ventana", 1.5, 1.1, 4, "Aluminio Módena", "Corrediza"],
            ["V2", "Ventana", 0.6, 0.6, 2, "Aluminio Módena", "Proyectante"],
            ["P1", "Puerta", 0.9, 2.05, 5, "Madera", "De abrir"],
            ["PV1", "Puerta ventana", 2.4, 2.2, 1, "Aluminio Módena", "Corrediza"],
        ]})), obra=obra, tipo=T.PLANILLAS, area=areas[A.DESARROLLO_PROYECTOS])

    rubros = [["Rubro", "Monto (ARS)"], ["Trabajos preliminares", 4200000], ["Movimiento de suelo", 6800000],
              ["Hormigón armado", 38500000], ["Mampostería", 17900000], ["Instalación sanitaria", 12300000],
              ["Instalación eléctrica", 11600000], ["Aberturas", 21400000],
              ["Revoques, pisos y terminaciones", 73700000], ["TOTAL", 186400000]]
    presupuesto, _ = services.crear_documento(
        admin, archivo("Presupuesto de obra v3.xlsx", _xlsx({"Resumen": rubros})),
        obra=obra, tipo=T.PRESUPUESTOS, area=areas[A.GESTION_ADMINISTRATIVA], titulo="Presupuesto de obra v3",
        monto=Decimal("186400000"), moneda="ARS", fecha_documento=date.today() - timedelta(days=20))
    services.cambiar_acceso(presupuesto, gerencia, Documento.Acceso.CLIENTE)

    services.crear_documento(
        admin, archivo("Costos internos y margenes.xlsx", _xlsx({"Costos": [
            ["Rubro", "Costo", "Margen %", "Precio"], ["Hormigón armado", 31200000, 23, 38500000],
            ["Aberturas", 17800000, 20, 21400000]]})),
        obra=obra, tipo=T.PRESUPUESTOS, area=areas[A.GESTION_ADMINISTRATIVA], acceso=Documento.Acceso.RESTRINGIDO,
        titulo="Costos internos y márgenes", etiquetas="confidencial")

    # Foto con fecha de toma, permiso con vencimiento y reporte de obra.
    foto, _ = services.crear_documento(
        jefe_obra, archivo("losa_planta_alta.jpg", _foto()), obra=obra, tipo=T.FOTOS,
        area=areas[A.GESTION_OBRAS], titulo="Hormigonado de losa de planta alta")
    services.cambiar_acceso(foto, jefe_obra, Documento.Acceso.CLIENTE)

    permiso, _ = services.crear_documento(
        jefe_obra, archivo("Permiso de obra.pdf", _pdf("Permiso de obra", [
            "Municipalidad de Pilar", "Expediente EXP-4021/2026", "Vivienda unifamiliar - 240 m2"])),
        obra=obra, tipo=T.PERMISOS, area=areas[A.GESTION_OBRAS], titulo="Permiso de obra municipal",
        organismo="Municipalidad de Pilar", numero="EXP-4021/2026",
        fecha_documento=date.today() - timedelta(days=150), vencimiento=date.today() + timedelta(days=25))
    services.cambiar_acceso(permiso, jefe_obra, Documento.Acceso.CLIENTE)

    services.crear_documento(
        jefe_obra, archivo("Reporte de obra 47.pdf", _pdf("Reporte diario de obra N 47", [
            "Clima: soleado", "Personal: 9", "Avance real 40% / previsto 42%"])),
        obra=obra, tipo=T.REPORTES, area=areas[A.GESTION_OBRAS], titulo="Reporte diario N° 47",
        numero="47", fecha_documento=date.today() - timedelta(days=1))

    # Biblioteca general del estudio.
    if not Documento.objects.filter(obra__isnull=True).exists():
        services.crear_documento(
            gerencia, archivo("Codigo de edificacion - extracto.pdf", _pdf("Código de Edificación (extracto)", [
                "Alturas mínimas de locales", "Iluminación y ventilación", "Medios de salida"])),
            obra=None, tipo=T.NORMATIVAS, area=areas[A.DIRECCION_TECNICA],
            titulo="Código de Edificación (extracto)", jurisdiccion="Provincia de Buenos Aires")
