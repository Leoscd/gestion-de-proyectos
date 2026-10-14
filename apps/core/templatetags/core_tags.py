from django import forms, template

register = template.Library()


@register.filter
def tipo_campo(campo):
    widget = campo.field.widget
    if isinstance(widget, forms.CheckboxSelectMultiple):
        return "casillas"
    if isinstance(widget, forms.RadioSelect):
        return "opciones"
    if isinstance(widget, forms.CheckboxInput):
        return "casilla"
    return "normal"


@register.filter
def bs(campo):
    """Renderiza el campo con las clases de Bootstrap que corresponden."""
    widget = campo.field.widget
    if isinstance(widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
        return campo
    if isinstance(widget, forms.CheckboxInput):
        clase = "form-check-input"
    elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
        clase = "form-select"
    else:
        clase = "form-control"
    if campo.errors:
        clase += " is-invalid"
    return campo.as_widget(attrs={"class": clase})


@register.filter
def tamano(bytes_):
    """1536 -> '1,5 KB'."""
    try:
        valor = float(bytes_)
    except (TypeError, ValueError):
        return ""
    for unidad in ("B", "KB", "MB", "GB"):
        if valor < 1024 or unidad == "GB":
            texto = f"{valor:.0f}" if unidad == "B" else f"{valor:.1f}"
            return f"{texto.replace('.', ',')} {unidad}"
        valor /= 1024
    return ""


@register.filter
def dinero(valor):
    """1234567.5 -> '1.234.567,50'."""
    if valor is None or valor == "":
        return ""
    texto = f"{float(valor):,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


@register.filter
def es_cambio(valor):
    """Un par [antes, después] guardado en el detalle del registro de actividad."""
    return isinstance(valor, list) and len(valor) == 2 and all(isinstance(v, str) for v in valor)


@register.filter
def es_lista(valor):
    return isinstance(valor, list)


ICONOS = {
    "pdf": "file-earmark-pdf text-danger",
    "xlsx": "file-earmark-spreadsheet text-success", "xlsm": "file-earmark-spreadsheet text-success",
    "xls": "file-earmark-spreadsheet text-success", "csv": "file-earmark-spreadsheet text-success",
    "jpg": "file-earmark-image text-primary", "jpeg": "file-earmark-image text-primary",
    "png": "file-earmark-image text-primary", "webp": "file-earmark-image text-primary",
    "heic": "file-earmark-image text-primary", "heif": "file-earmark-image text-primary",
    "doc": "file-earmark-word text-primary", "docx": "file-earmark-word text-primary",
    "dwg": "file-earmark-ruled", "dxf": "file-earmark-ruled", "rvt": "box", "ifc": "box", "skp": "box",
    "mpp": "calendar3-range",
}


@register.filter
def icono_archivo(extension):
    return ICONOS.get(str(extension).lower(), "file-earmark")


@register.simple_tag(takes_context=True)
def query_con(context, **cambios):
    """Arma el querystring actual cambiando algunos parámetros (para filtros y paginación)."""
    params = context["request"].GET.copy()
    for clave, valor in cambios.items():
        if valor in (None, ""):
            params.pop(clave, None)
        else:
            params[clave] = valor
    return params.urlencode()
