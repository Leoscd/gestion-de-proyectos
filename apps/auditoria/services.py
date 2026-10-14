from django.conf import settings

from .middleware import request_actual
from .models import RegistroActividad


def ip_de(request):
    if request is None:
        return None
    if settings.CONFIAR_EN_PROXY:
        reenviada = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if reenviada:
            return reenviada.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def _obra_de(objeto):
    from apps.obras.models import Obra

    if isinstance(objeto, Obra):
        return objeto
    return getattr(objeto, "obra", None)


def registrar(accion, descripcion, *, usuario=None, objeto=None, obra=None, detalle=None, request=None):
    """Asienta una acción en el registro de actividad.

    Si no se pasa `usuario` ni `request`, los toma del request en curso.
    La obra se deduce del objeto cuando este tiene un atributo `obra`.
    """
    request = request or request_actual()
    if usuario is None and request is not None and request.user.is_authenticated:
        usuario = request.user
    if obra is None and objeto is not None:
        obra = _obra_de(objeto)

    return RegistroActividad.objects.create(
        usuario=usuario,
        usuario_nombre=(usuario.nombre_completo if usuario else "Sistema")[:200],
        accion=accion,
        descripcion=descripcion[:300],
        obra=obra,
        objeto_tipo=objeto._meta.verbose_name[:60] if objeto is not None else "",
        objeto_id=str(objeto.pk) if objeto is not None else "",
        objeto_repr=str(objeto)[:200] if objeto is not None else "",
        detalle=detalle or {},
        ip=ip_de(request),
    )
