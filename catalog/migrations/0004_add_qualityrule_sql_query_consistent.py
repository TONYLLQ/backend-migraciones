# Generated manually to add consistent SQL query to QualityRule

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_alter_actiontype_id_alter_ruledimension_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="qualityrule",
            name="sql_query_consistent",
            field=models.TextField(blank=True, null=True),
        ),
    ]
