from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Administración técnica"
admin.site.site_title = "Administración técnica"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuenta/", include("django.contrib.auth.urls")),
    path("", include("apps.core.urls")),
    path("personal/", include("apps.cuentas.urls")),
    # Se activan a medida que se construye cada sección:
    path("obras/", include("apps.obras.urls")),
    path("documentos/", include("apps.documentos.urls")),
    # path("solicitudes/", include("apps.aprobaciones.urls")),
    # path("notificaciones/", include("apps.notificaciones.urls")),
    # path("comunicados/", include("apps.comunicados.urls")),
    # path("actividad/", include("apps.auditoria.urls")),
    # path("portal/", include("apps.portal.urls")),
]
