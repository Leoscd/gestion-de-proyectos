from django.conf import settings
from django.db import models
from django.utils import timezone


class RegistroInmutable(Exception):
    """El registro de actividad solo admite agregar filas."""


class RegistroQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise RegistroInmutable("El registro de actividad no se puede modificar.")

    def delete(self):
        raise RegistroInmutable("El registro de actividad no se puede borrar.")


class RegistroActividad(models.Model):
    """Asiento de una acción hecha en el sistema.

    Es de solo agregar: no se edita ni se borra (ni desde la app, ni desde el
    admin, ni por SQL: la migración 0002 agrega triggers en la base).
    Los usuarios y obras referenciados quedan protegidos contra el borrado;
    para dar de baja a alguien se lo desactiva.
    """

    fecha = models.DateTimeField(default=timezone.now, db_index=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name="actividad",
    )
    usuario_nombre = models.CharField("usuario (al momento)", max_length=200, blank=True)
    accion = models.CharField(max_length=60, db_index=True)
    descripcion = models.CharField(max_length=300)
    obra = models.ForeignKey(
        "obras.Obra", null=True, blank=True, on_delete=models.PROTECT, related_name="actividad",
    )
    objeto_tipo = models.CharField(max_length=60, blank=True)
    objeto_id = models.CharField(max_length=40, blank=True)
    objeto_repr = models.CharField(max_length=200, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    objects = RegistroQuerySet.as_manager()

    class Meta:
        verbose_name = "registro de actividad"
        verbose_name_plural = "registro de actividad"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.fecha:%d/%m/%Y %H:%M} · {self.usuario_nombre or 'Sistema'} · {self.descripcion}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise RegistroInmutable("El registro de actividad no se puede modificar.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistroInmutable("El registro de actividad no se puede borrar.")
