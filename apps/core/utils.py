"""Utilidades compartidas entre secciones."""


def cambios_de_formulario(form):
    """{campo: [antes, después]} de los campos que cambió el formulario, en texto legible."""
    cambios = {}
    for campo in form.changed_data:
        antes = form.initial.get(campo)
        despues = form.cleaned_data.get(campo)
        bound = form[campo]
        if hasattr(bound.field, "choices") and not hasattr(bound.field, "queryset"):
            opciones = dict(bound.field.choices)
            antes, despues = opciones.get(antes, antes), opciones.get(despues, despues)
        if hasattr(bound.field, "queryset") and antes is not None:
            antes = bound.field.queryset.model.objects.filter(pk=antes).first()
        cambios[form.fields[campo].label or campo] = [str(antes if antes is not None else "—"),
                                                     str(despues if despues not in (None, "") else "—")]
    return cambios
