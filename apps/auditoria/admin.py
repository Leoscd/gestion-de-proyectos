from django.contrib import admin

from .models import RegistroActividad


@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    list_display = ("fecha", "usuario_nombre", "accion", "descripcion", "obra", "ip")
    list_filter = ("accion", "obra")
    search_fields = ("descripcion", "usuario_nombre", "objeto_repr")
    date_hierarchy = "fecha"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
