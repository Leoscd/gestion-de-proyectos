from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class Obra(models.Model):
    class Etapa(models.TextChoices):
        ANTEPROYECTO = "anteproyecto", "Anteproyecto"
        PROYECTO = "proyecto", "Proyecto"
        DOCUMENTACION = "documentacion", "Documentación"
        LICITACION = "licitacion", "Licitación"
        EJECUCION = "ejecucion", "En ejecución"
        ENTREGA = "entrega", "Entrega"

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        PAUSADA = "pausada", "Pausada"
        FINALIZADA = "finalizada", "Finalizada"

    codigo = models.CharField("código", max_length=20, unique=True, blank=True,
                              help_text="Si lo dejás vacío se genera solo (OB-AÑO-NNN).")
    nombre = models.CharField(max_length=200)
    cliente = models.ForeignKey("cuentas.Cliente", on_delete=models.PROTECT, related_name="obras")
    direccion = models.CharField("dirección", max_length=200, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField("descripción", blank=True)
    superficie_m2 = models.DecimalField("superficie (m²)", max_digits=10, decimal_places=2, null=True, blank=True)
    etapa = models.CharField(max_length=20, choices=Etapa.choices, default=Etapa.ANTEPROYECTO)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ACTIVA)
    fecha_inicio = models.DateField("fecha de inicio", null=True, blank=True)
    fecha_fin_estimada = models.DateField("fin estimado", null=True, blank=True)
    avance = models.PositiveSmallIntegerField("avance (%)", default=0, validators=[MaxValueValidator(100)])
    equipo = models.ManyToManyField(settings.AUTH_USER_MODEL, through="AsignacionObra", related_name="obras")
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="+")
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada"]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}" if self.codigo else self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._siguiente_codigo()
        super().save(*args, **kwargs)

    @staticmethod
    def _siguiente_codigo():
        prefijo = f"OB-{date.today().year}-"
        ultimos = Obra.objects.filter(codigo__startswith=prefijo).values_list("codigo", flat=True)
        numeros = [int(c.rsplit("-", 1)[1]) for c in ultimos if c.rsplit("-", 1)[1].isdigit()]
        return f"{prefijo}{(max(numeros, default=0) + 1):03d}"


class AsignacionObra(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name="asignaciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="asignaciones",
                                limit_choices_to={"tipo": "personal", "is_active": True})
    area = models.ForeignKey("cuentas.Area", on_delete=models.PROTECT, related_name="asignaciones")
    funcion = models.CharField("función en la obra", max_length=100, blank=True,
                               help_text="Ej: Director de obra, Proyectista, Compras.")
    es_responsable = models.BooleanField("responsable en la obra", default=False,
                                         help_text="Puede editar los datos de la obra y su equipo.")
    desde = models.DateField(default=date.today)

    class Meta:
        verbose_name = "asignación a obra"
        verbose_name_plural = "asignaciones a obras"
        ordering = ["area__orden", "usuario__first_name"]
        constraints = [
            models.UniqueConstraint(fields=["obra", "usuario", "area"], name="asignacion_unica"),
        ]

    def __str__(self):
        return f"{self.usuario} en {self.obra} ({self.area})"


class Hito(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name="hitos")
    titulo = models.CharField("título", max_length=200)
    fecha = models.DateField()
    completado = models.BooleanField(default=False)
    visible_cliente = models.BooleanField("visible para el cliente", default=True)

    class Meta:
        ordering = ["fecha", "id"]

    def __str__(self):
        return f"{self.titulo} ({self.fecha:%d/%m/%Y})"
