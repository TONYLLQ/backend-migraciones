# Generated manually to add validation fields to ScenarioDocument

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("scenarios", "0008_remove_rule_from_scenariodocument"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenariodocument",
            name="is_validated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scenariodocument",
            name="validated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scenariodocument",
            name="validated_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="validated_scenario_documents", to="accounts.user"),
        ),
    ]
