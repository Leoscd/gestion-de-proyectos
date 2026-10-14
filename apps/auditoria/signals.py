from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .services import registrar


@receiver(user_logged_in)
def al_ingresar(sender, request, user, **kwargs):
    registrar("sesion.ingreso", "Ingresó al sistema", usuario=user, request=request)


@receiver(user_logged_out)
def al_salir(sender, request, user, **kwargs):
    if user is not None:
        registrar("sesion.salida", "Salió del sistema", usuario=user, request=request)


@receiver(user_login_failed)
def al_fallar_ingreso(sender, credentials, request=None, **kwargs):
    email = (credentials or {}).get("username") or (credentials or {}).get("email") or ""
    registrar(
        "sesion.fallida", f"Intento de ingreso fallido ({email})"[:300],
        request=request, detalle={"email": email},
    )
