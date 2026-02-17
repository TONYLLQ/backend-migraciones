# Generated manually to allow analysts to transition REGISTERED -> ASSIGNED

from django.db import migrations


def forwards_func(apps, schema_editor):
    ScenarioStatus = apps.get_model("catalog", "ScenarioStatus")
    ScenarioTransition = apps.get_model("catalog", "ScenarioTransition")

    registered = ScenarioStatus.objects.filter(code__in=["REGISTERED", "REGISTRADO"]).first()
    assigned = ScenarioStatus.objects.filter(code__in=["ASSIGNED", "ASIGNADO"]).first()
    if not registered or not assigned:
        return

    transition = ScenarioTransition.objects.filter(
        from_status_id=registered.id,
        to_status_id=assigned.id,
    ).first()

    if transition:
        transition.allow_analyst = True
        transition.is_active = True
        transition.save(update_fields=["allow_analyst", "is_active"])
    else:
        ScenarioTransition.objects.create(
            from_status_id=registered.id,
            to_status_id=assigned.id,
            allow_coordinator=True,
            allow_analyst=True,
            allow_viewer=False,
            is_active=True,
        )


def backwards_func(apps, schema_editor):
    ScenarioStatus = apps.get_model("catalog", "ScenarioStatus")
    ScenarioTransition = apps.get_model("catalog", "ScenarioTransition")

    registered = ScenarioStatus.objects.filter(code__in=["REGISTERED", "REGISTRADO"]).first()
    assigned = ScenarioStatus.objects.filter(code__in=["ASSIGNED", "ASIGNADO"]).first()
    if not registered or not assigned:
        return

    transition = ScenarioTransition.objects.filter(
        from_status_id=registered.id,
        to_status_id=assigned.id,
    ).first()
    if transition:
        transition.allow_analyst = False
        transition.save(update_fields=["allow_analyst"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_alter_actiontype_id_alter_ruledimension_id_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
