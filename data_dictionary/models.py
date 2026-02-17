from django.db import models
from catalog.models import QualityRule


class TableCatalog(models.Model):
    name = models.CharField(max_length=200, unique=True)
    schema = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    source_system = models.CharField(max_length=120, blank=True, null=True)
    owner = models.CharField(max_length=120, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.schema + '.' if self.schema else ''}{self.name}"


class DataType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class TableField(models.Model):
    table = models.ForeignKey(TableCatalog, on_delete=models.CASCADE, related_name="fields")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    data_type = models.ForeignKey(
        DataType,
        on_delete=models.PROTECT,
        related_name="fields",
        blank=True,
        null=True,
    )
    is_nullable = models.BooleanField(default=True)
    is_primary_key = models.BooleanField(default=False)
    is_foreign_key = models.BooleanField(default=False)
    max_length = models.IntegerField(blank=True, null=True)
    precision = models.IntegerField(blank=True, null=True)
    scale = models.IntegerField(blank=True, null=True)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    is_indexed = models.BooleanField(default=False)
    analysis_required = models.BooleanField(default=False)
    analysis_notes = models.TextField(blank=True, null=True)
    sample_values = models.TextField(blank=True, null=True)
    last_verified_at = models.DateTimeField(blank=True, null=True)
    analysis_rules = models.ManyToManyField(QualityRule, blank=True, related_name="analysis_fields")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["table", "name"]
        unique_together = ("table", "name")

    def __str__(self):
        return f"{self.table}::{self.name}"
