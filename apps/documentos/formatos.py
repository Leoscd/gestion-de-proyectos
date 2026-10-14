"""Qué formatos acepta cada tipo de documento."""

import os

from django.conf import settings

from .models import Documento

T = Documento.Tipo

EDITABLES = {".dwg", ".dxf", ".rvt", ".rfa", ".ifc", ".skp", ".3dm"}
IMAGENES = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
PLANILLAS = {".xlsx", ".xlsm", ".xls", ".csv"}

FORMATOS = {
    T.PLANOS: {".pdf"},
    T.PLANILLAS: PLANILLAS,
    T.PRESUPUESTOS: PLANILLAS | {".pdf"},
    T.CRONOGRAMAS: PLANILLAS | {".mpp", ".pdf"},
    T.REPORTES: {".pdf"},
    T.FOTOS: IMAGENES,
    T.PERMISOS: {".pdf", ".jpg", ".jpeg", ".png"},
    T.NORMATIVAS: {".pdf"},
    T.CONTRATOS: {".pdf", ".docx", ".doc"},
    T.OTROS: None,  # cualquiera menos los bloqueados
}


def extension(nombre):
    return os.path.splitext(nombre)[1].lower()


def descripcion_formatos(tipo):
    permitidos = FORMATOS.get(tipo)
    if permitidos is None:
        return "Cualquier formato (menos ejecutables)"
    texto = ", ".join(sorted(e.lstrip(".").upper() for e in permitidos))
    if tipo == T.PLANOS:
        texto += " (y opcionalmente el editable: DWG, DXF, RVT, IFC, SKP)"
    return texto


def validar(tipo, archivo, editable=False):
    """Devuelve un mensaje de error, o None si el archivo se puede subir."""
    ext = extension(archivo.name)
    if ext in settings.EXTENSIONES_BLOQUEADAS or not ext:
        return f"«{archivo.name}»: ese tipo de archivo no está permitido."
    maximo = settings.MAX_ARCHIVO_MB * 1024 * 1024
    if archivo.size > maximo:
        return f"«{archivo.name}» pesa más de {settings.MAX_ARCHIVO_MB} MB."
    if editable:
        if ext not in EDITABLES:
            return f"«{archivo.name}»: el editable tiene que ser DWG, DXF, RVT, RFA, IFC, SKP o 3DM."
        return None
    permitidos = FORMATOS.get(tipo)
    if permitidos is not None and ext not in permitidos:
        return f"«{archivo.name}»: en {Documento.Tipo(tipo).label} se aceptan {descripcion_formatos(tipo)}."
    return None
