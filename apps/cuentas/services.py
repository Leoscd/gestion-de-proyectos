from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.auditoria.services import registrar


def enlace_para_elegir_clave(usuario):
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    return settings.SITIO_URL + reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})


def enviar_invitacion(usuario):
    contexto = {
        "usuario": usuario,
        "estudio": settings.NOMBRE_ESTUDIO,
        "enlace": enlace_para_elegir_clave(usuario),
        "sitio": settings.SITIO_URL,
    }
    send_mail(
        f"Te damos la bienvenida a {settings.NOMBRE_ESTUDIO}",
        render_to_string("cuentas/email/invitacion.txt", contexto),
        None,
        [usuario.email],
    )
    registrar("usuario.invitacion", f"Se envió invitación a {usuario.nombre_completo}", objeto=usuario)
