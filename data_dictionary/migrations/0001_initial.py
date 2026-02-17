# Generated manually for data_dictionary app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0003_alter_actiontype_id_alter_ruledimension_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TableCatalog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("schema", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("source_system", models.CharField(blank=True, max_length=120, null=True)),
                ("owner", models.CharField(blank=True, max_length=120, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, null=True)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TableField",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, null=True)),
                ("data_type", models.CharField(blank=True, max_length=100, null=True)),
                ("is_nullable", models.BooleanField(default=True)),
                ("is_primary_key", models.BooleanField(default=False)),
                ("is_foreign_key", models.BooleanField(default=False)),
                ("max_length", models.IntegerField(blank=True, null=True)),
                ("precision", models.IntegerField(blank=True, null=True)),
                ("scale", models.IntegerField(blank=True, null=True)),
                ("default_value", models.CharField(blank=True, max_length=255, null=True)),
                ("is_indexed", models.BooleanField(default=False)),
                ("analysis_required", models.BooleanField(default=False)),
                ("analysis_notes", models.TextField(blank=True, null=True)),
                ("sample_values", models.TextField(blank=True, null=True)),
                ("last_verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("table", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fields", to="data_dictionary.tablecatalog")),
            ],
            options={
                "ordering": ["table", "name"],
                "unique_together": {("table", "name")},
            },
        ),
        migrations.AddField(
            model_name="tablefield",
            name="analysis_rules",
            field=models.ManyToManyField(blank=True, related_name="analysis_fields", to="catalog.qualityrule"),
        ),
    ]
