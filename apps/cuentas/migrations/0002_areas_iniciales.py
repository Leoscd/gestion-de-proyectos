from django.db import migrations

AREAS = [
    ("gerencia", "Gerencia", "Dirección general del estudio. Ve y administra todas las obras.", 1),
    ("gestion_obras", "Gestión de Obras", "Avance en obra, bitácora, fotos y cronograma de ejecución.", 2),
    ("gestion_administrativa", "Gestión Administrativa", "Presupuestos, gastos, facturación y clientes.", 3),
    ("gestion_proyectos", "Gestión de Proyectos", "Coordinación, cronograma y decisiones con el cliente.", 4),
    ("desarrollo_proyectos", "Desarrollo de Proyectos", "Planos y documentación técnica.", 5),
    ("direccion_tecnica", "Dirección Técnica", "Normativas y visto bueno técnico antes de enviar al cliente.", 6),
]


def crear_areas(apps, schema_editor):
    Area = apps.get_model("cuentas", "Area")
    for codigo, nombre, descripcion, orden in AREAS:
        Area.objects.update_or_create(
            codigo=codigo, defaults={"nombre": nombre, "descripcion": descripcion, "orden": orden}
        )


class Migration(migrations.Migration):
    dependencies = [("cuentas", "0001_initial")]

    operations = [migrations.RunPython(crear_areas, migrations.RunPython.noop)]
