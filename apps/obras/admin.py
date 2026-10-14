from django.contrib import admin

from .models import AsignacionObra, Hito, Obra


class AsignacionInline(admin.TabularInline):
    model = AsignacionObra
    extra = 0


class HitoInline(admin.TabularInline):
    model = Hito
    extra = 0


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "cliente", "etapa", "estado", "avance")
    list_filter = ("estado", "etapa")
    search_fields = ("codigo", "nombre", "cliente__nombre")
    inlines = [AsignacionInline, HitoInline]
