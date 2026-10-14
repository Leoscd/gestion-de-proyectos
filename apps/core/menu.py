"""Menú lateral. Cada ítem: (nombre de url, texto, ícono bootstrap, permiso requerido).

Los ítems cuyo url todavía no existe se omiten solos, así el menú crece a
medida que se agregan secciones.
"""

from django.urls import NoReverseMatch, reverse

MENU_PERSONAL = [
    ("Principal", [
        ("core:tablero", "Tablero", "speedometer2", None),
        ("obras:lista", "Obras", "buildings", None),
        ("documentos:lista", "Archivos", "folder2-open", None),
        ("aprobaciones:lista", "Solicitudes al cliente", "check2-square", None),
        ("comunicados:lista", "Comunicados", "megaphone", None),
        ("notificaciones:lista", "Notificaciones", "bell", None),
    ]),
    ("Organización", [
        ("cuentas:areas", "Áreas y equipos", "diagram-3", None),
        ("cuentas:personal", "Personal", "people", "gerencia"),
        ("cuentas:clientes", "Clientes", "person-vcard", "clientes"),
        ("auditoria:lista", "Registro de actividad", "journal-text", "auditoria"),
    ]),
]

MENU_CLIENTE = [
    ("portal:inicio", "Mis obras", "house", None),
    ("portal:solicitudes", "Aprobaciones", "check2-square", None),
    ("comunicados:recibidos", "Mensajes", "envelope", None),
    ("notificaciones:lista", "Notificaciones", "bell", None),
]


def _item(request, nombre_url, texto, icono):
    try:
        url = reverse(nombre_url)
    except NoReverseMatch:
        return None
    activo = request.path == url if url == "/" else request.path.startswith(url)
    return {"url": url, "texto": texto, "icono": icono, "activo": activo}


def construir_menu(request, perm):
    if perm.get("cliente"):
        items = [_item(request, u, t, i) for u, t, i, _ in MENU_CLIENTE]
        return [{"titulo": "", "items": [x for x in items if x]}]
    menu = []
    for titulo, entradas in MENU_PERSONAL:
        items = [
            _item(request, u, t, i) for u, t, i, requiere in entradas
            if requiere is None or perm.get(requiere)
        ]
        items = [x for x in items if x]
        if items:
            menu.append({"titulo": titulo, "items": items})
    return menu
