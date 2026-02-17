# Generated manually to support multiple documents by stage/rule

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("scenarios", "0006_alter_operationalactionstatus_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScenarioDocument",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("file", models.FileField(upload_to="scenarios/docs/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("scenario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="scenarios.scenario")),
                ("status", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="scenario_documents", to="catalog.scenariostatus")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="uploaded_scenario_documents", to="accounts.user")),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
