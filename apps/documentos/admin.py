from django.contrib import admin

from .models import Documento, VersionDocumento


class VersionInline(admin.TabularInline):
    model = VersionDocumento
    extra = 0
    fields = ("revision", "nombre_original", "tamano", "sha256", "subido_por", "subido_en", "aprobada_en")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "numero", "tipo", "obra", "acceso", "archivado", "en_papelera", "actualizado")
    list_filter = ("tipo", "acceso", "archivado", "en_papelera")
    search_fields = ("titulo", "numero", "etiquetas")
    inlines = [VersionInline]

    def has_delete_permission(self, request, obj=None):
        return False  # el borrado definitivo se hace desde la papelera, para que quede asentado
