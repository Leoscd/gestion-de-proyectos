from datetime import date

from django.apps import apps
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.auditoria.services import registrar
from apps.core.utils import cambios_de_formulario as _cambios
from apps.cuentas import permisos

from .forms import AsignacionForm, HitoForm, ObraForm
from .models import AsignacionObra, Hito, Obra

PESTANAS = [
    ("resumen", "Resumen", "info-circle"),
    ("equipo", "Equipo", "people"),
    ("hitos", "Hitos", "flag"),
    ("archivos", "Archivos", "folder2-open"),
    ("solicitudes", "Solicitudes", "check2-square"),
    ("actividad", "Actividad", "journal-text"),
]
# Pestañas que dependen de secciones que todavía pueden no estar activas.
PESTANA_APP = {"archivos": "apps.documentos", "solicitudes": "apps.aprobaciones"}


def _obra_visible(request, pk):
    obra = get_object_or_404(Obra.objects.select_related("cliente"), pk=pk)
    permisos.exigir(permisos.puede_ver_obra(request.user, obra))
    return obra


def _exigir_edicion(request, obra):
    permisos.exigir(permisos.puede_editar_obra(request.user, obra))


@permisos.solo_personal
def lista(request):
    estado = request.GET.get("estado", Obra.Estado.ACTIVA)
    etapa = request.GET.get("etapa", "")
    q = request.GET.get("q", "").strip()
    obras = (permisos.obras_visibles(request.user).select_related("cliente")
             .annotate(personas=Count("asignaciones__usuario", distinct=True)))
    if estado:
        obras = obras.filter(estado=estado)
    if etapa:
        obras = obras.filter(etapa=etapa)
    if q:
        obras = obras.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(cliente__nombre__icontains=q)
                             | Q(localidad__icontains=q))
    return render(request, "obras/lista.html", {
        "obras": obras.order_by("nombre"),
        "estado": estado, "etapa": etapa, "q": q,
        "estados": Obra.Estado.choices, "etapas": Obra.Etapa.choices,
        "puede_crear": permisos.puede_crear_obra(request.user),
    })


@permisos.solo_personal
def obra_form(request, pk=None):
    obra = None
    if pk:
        obra = _obra_visible(request, pk)
        _exigir_edicion(request, obra)
    else:
        permisos.exigir(permisos.puede_crear_obra(request.user))
    form = ObraForm(request.POST or None, instance=obra, initial={} if obra else {
        "cliente": request.GET.get("cliente")})
    if request.method == "POST" and form.is_valid():
        es_alta = obra is None
        cambios = {} if es_alta else _cambios(form)
        obra = form.save(commit=False)
        if es_alta:
            obra.creada_por = request.user
        obra.save()
        if es_alta:
            registrar("obra.alta", f"Alta de obra: {obra}", objeto=obra)
            messages.success(request, f"Obra {obra.codigo} creada. Ahora sumá a su equipo.")
            return redirect(f"{obra_url(obra)}?tab=equipo")
        if cambios:
            registrar("obra.edicion", f"Edición de obra: {', '.join(cambios)}", objeto=obra, detalle=cambios)
        messages.success(request, "Los datos de la obra quedaron guardados.")
        return redirect(obra_url(obra))
    return render(request, "obras/form.html", {"form": form, "obra": obra})


def obra_url(obra):
    from django.urls import reverse

    return reverse("obras:detalle", args=[obra.pk])


@permisos.solo_personal
def detalle(request, pk):
    obra = _obra_visible(request, pk)
    puede_editar = permisos.puede_editar_obra(request.user, obra)
    pestanas = [p for p in PESTANAS if p[0] not in PESTANA_APP or apps.is_installed(PESTANA_APP[p[0]])]
    tab = request.GET.get("tab", "resumen")
    if tab not in {p[0] for p in pestanas}:
        tab = "resumen"

    asignaciones = obra.asignaciones.select_related("usuario", "area")
    hitos = obra.hitos.all()
    contexto = {
        "obra": obra, "tab": tab, "pestanas": pestanas, "puede_editar": puede_editar, "hoy": date.today(),
        "asignaciones": asignaciones, "hitos": hitos,
        "personas_equipo": len({a.usuario_id for a in asignaciones}),
        "proximo_hito": hitos.filter(completado=False).first(),
        "hitos_hechos": sum(1 for h in hitos if h.completado),
    }
    if tab == "equipo" and puede_editar:
        contexto["form_asignacion"] = AsignacionForm(obra=obra)
    if tab == "hitos" and puede_editar:
        contexto["form_hito"] = HitoForm()
    if tab == "archivos":
        from apps.documentos.views import contexto_pestana_obra

        contexto.update(contexto_pestana_obra(request, obra))
    if tab == "actividad":
        pagina = Paginator(obra.actividad.select_related("usuario"), 40).get_page(request.GET.get("pagina"))
        contexto["pagina"] = pagina
    return render(request, "obras/detalle.html", contexto)


# --- Equipo ------------------------------------------------------------------

@permisos.solo_personal
@require_POST
def equipo_agregar(request, pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    form = AsignacionForm(request.POST, obra=obra)
    if form.is_valid():
        a = form.save()
        registrar("obra.equipo_alta", f"Se sumó a {a.usuario.nombre_completo} por {a.area.nombre}", objeto=obra,
                  detalle={"persona": a.usuario.email, "area": a.area.nombre, "funcion": a.funcion,
                           "responsable": a.es_responsable})
        messages.success(request, f"{a.usuario.nombre_completo} se sumó al equipo.")
    else:
        for errores in form.errors.values():
            for e in errores:
                messages.error(request, e)
    return redirect(f"{obra_url(obra)}?tab=equipo")


@permisos.solo_personal
@require_POST
def equipo_quitar(request, pk, asignacion_pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    a = get_object_or_404(AsignacionObra, pk=asignacion_pk, obra=obra)
    if a.es_responsable and not obra.asignaciones.filter(es_responsable=True).exclude(pk=a.pk).exists() \
            and not permisos.es_gerencia(request.user):
        messages.error(request, "No podés quitar al único responsable de la obra. Pedíselo a Gerencia.")
        return redirect(f"{obra_url(obra)}?tab=equipo")
    registrar("obra.equipo_baja", f"Se quitó a {a.usuario.nombre_completo} ({a.area.nombre})", objeto=obra,
              detalle={"persona": a.usuario.email, "area": a.area.nombre})
    a.delete()
    messages.success(request, f"{a.usuario.nombre_completo} ya no está en el equipo de la obra.")
    return redirect(f"{obra_url(obra)}?tab=equipo")


@permisos.solo_personal
@require_POST
def equipo_responsable(request, pk, asignacion_pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    a = get_object_or_404(AsignacionObra, pk=asignacion_pk, obra=obra)
    a.es_responsable = not a.es_responsable
    a.save(update_fields=["es_responsable"])
    registrar("obra.equipo_responsable",
              f"{a.usuario.nombre_completo} {'pasó a ser' if a.es_responsable else 'dejó de ser'} responsable de la obra",
              objeto=obra)
    return redirect(f"{obra_url(obra)}?tab=equipo")


# --- Hitos -------------------------------------------------------------------

@permisos.solo_personal
@require_POST
def hito_agregar(request, pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    form = HitoForm(request.POST)
    if form.is_valid():
        hito = form.save(commit=False)
        hito.obra = obra
        hito.save()
        registrar("obra.hito_alta", f"Nuevo hito: {hito}", objeto=obra)
        messages.success(request, "Hito agregado.")
    else:
        messages.error(request, "Completá el título y la fecha del hito.")
    return redirect(f"{obra_url(obra)}?tab=hitos")


@permisos.solo_personal
@require_POST
def hito_alternar(request, pk, hito_pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    hito = get_object_or_404(Hito, pk=hito_pk, obra=obra)
    hito.completado = not hito.completado
    hito.save(update_fields=["completado"])
    registrar("obra.hito_estado", f"Hito {'cumplido' if hito.completado else 'reabierto'}: {hito}", objeto=obra)
    return redirect(f"{obra_url(obra)}?tab=hitos")


@permisos.solo_personal
@require_POST
def hito_borrar(request, pk, hito_pk):
    obra = _obra_visible(request, pk)
    _exigir_edicion(request, obra)
    hito = get_object_or_404(Hito, pk=hito_pk, obra=obra)
    registrar("obra.hito_baja", f"Se quitó el hito: {hito}", objeto=obra)
    hito.delete()
    messages.success(request, "Hito quitado.")
    return redirect(f"{obra_url(obra)}?tab=hitos")
