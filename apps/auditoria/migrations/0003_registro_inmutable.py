"""Triggers que impiden modificar o borrar el registro de actividad desde la base."""

from django.db import migrations

TABLA = "auditoria_registroactividad"

SQLITE_CREAR = [
    f"""CREATE TRIGGER IF NOT EXISTS {TABLA}_sin_update BEFORE UPDATE ON {TABLA}
        BEGIN SELECT RAISE(ABORT, 'El registro de actividad es inmutable'); END;""",
    f"""CREATE TRIGGER IF NOT EXISTS {TABLA}_sin_delete BEFORE DELETE ON {TABLA}
        BEGIN SELECT RAISE(ABORT, 'El registro de actividad es inmutable'); END;""",
]
SQLITE_BORRAR = [
    f"DROP TRIGGER IF EXISTS {TABLA}_sin_update;",
    f"DROP TRIGGER IF EXISTS {TABLA}_sin_delete;",
]

POSTGRES_CREAR = [
    """CREATE OR REPLACE FUNCTION registro_inmutable() RETURNS trigger AS $$
       BEGIN RAISE EXCEPTION 'El registro de actividad es inmutable'; END;
       $$ LANGUAGE plpgsql;""",
    f"""CREATE TRIGGER {TABLA}_inmutable BEFORE UPDATE OR DELETE ON {TABLA}
        FOR EACH ROW EXECUTE FUNCTION registro_inmutable();""",
]
POSTGRES_BORRAR = [
    f"DROP TRIGGER IF EXISTS {TABLA}_inmutable ON {TABLA};",
    "DROP FUNCTION IF EXISTS registro_inmutable();",
]


def _ejecutar(schema_editor, por_motor):
    for sentencia in por_motor.get(schema_editor.connection.vendor, []):
        schema_editor.execute(sentencia)


def crear(apps, schema_editor):
    _ejecutar(schema_editor, {"sqlite": SQLITE_CREAR, "postgresql": POSTGRES_CREAR})


def borrar(apps, schema_editor):
    _ejecutar(schema_editor, {"sqlite": SQLITE_BORRAR, "postgresql": POSTGRES_BORRAR})


class Migration(migrations.Migration):
    dependencies = [("auditoria", "0002_initial")]

    operations = [migrations.RunPython(crear, borrar)]
