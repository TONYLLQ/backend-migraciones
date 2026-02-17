# Generated manually to add DataType catalog and link TableField.data_type

from django.db import migrations, models
import django.db.models.deletion
import re


def _normalize_code(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "UNKNOWN"


def forwards_func(apps, schema_editor):
    DataType = apps.get_model("data_dictionary", "DataType")
    TableField = apps.get_model("data_dictionary", "TableField")

    seen = {}
    order = 0

    for field in TableField.objects.exclude(data_type__isnull=True).exclude(data_type__exact=""):
        raw = field.data_type
        code = _normalize_code(raw)
        if code not in seen:
            dt, _ = DataType.objects.get_or_create(code=code, defaults={
                "name": raw.strip(),
                "is_active": True,
                "order": order,
            })
            seen[code] = dt
            order += 1
        field.data_type_fk_id = seen[code].id
        field.save(update_fields=["data_type_fk"])


def backwards_func(apps, schema_editor):
    DataType = apps.get_model("data_dictionary", "DataType")
    TableField = apps.get_model("data_dictionary", "TableField")

    for field in TableField.objects.exclude(data_type_fk__isnull=True):
        dt = DataType.objects.filter(id=field.data_type_fk_id).first()
        if dt:
            field.data_type = dt.name
            field.save(update_fields=["data_type"])


class Migration(migrations.Migration):

    dependencies = [
        ("data_dictionary", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataType",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
        migrations.AddField(
            model_name="tablefield",
            name="data_type_fk",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="fields", to="data_dictionary.datatype"),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.RemoveField(
            model_name="tablefield",
            name="data_type",
        ),
        migrations.RenameField(
            model_name="tablefield",
            old_name="data_type_fk",
            new_name="data_type",
        ),
    ]
