from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    name = "apps.auditoria"
    verbose_name = "Registro de actividad"

    def ready(self):
        from . import signals  # noqa: F401
