from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import Area, Cliente, MiembroArea, Usuario


class UsuarioCreationForm(BaseUserCreationForm):
    class Meta:
        model = Usuario
        fields = ("email", "tipo")


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = "__all__"


class MiembroAreaInline(admin.TabularInline):
    model = MiembroArea
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "tipo", "cliente", "is_active")
    list_filter = ("tipo", "is_active", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    inlines = [MiembroAreaInline]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos", {"fields": ("first_name", "last_name", "tipo", "cargo", "telefono", "cliente")}),
        ("Avisos", {"fields": ("notif_email", "notif_whatsapp")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "tipo", "usable_password", "password1", "password2")}),)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cuit", "email", "telefono")
    search_fields = ("nombre", "cuit", "email")


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "orden")
    inlines = [MiembroAreaInline]

    def has_delete_permission(self, request, obj=None):
        return False
