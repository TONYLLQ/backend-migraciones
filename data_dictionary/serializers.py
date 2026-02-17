from rest_framework import serializers
from catalog.models import QualityRule
from .models import TableCatalog, TableField, DataType


class TableFieldSerializer(serializers.ModelSerializer):
    data_type_code = serializers.CharField(source="data_type.code", read_only=True)
    data_type_name = serializers.CharField(source="data_type.name", read_only=True)
    analysis_rules = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QualityRule.objects.all(),
        required=False,
    )

    class Meta:
        model = TableField
        fields = [
            "id",
            "table",
            "name",
            "description",
            "data_type",
            "data_type_code",
            "data_type_name",
            "is_nullable",
            "is_primary_key",
            "is_foreign_key",
            "max_length",
            "precision",
            "scale",
            "default_value",
            "is_indexed",
            "analysis_required",
            "analysis_notes",
            "sample_values",
            "last_verified_at",
            "analysis_rules",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DataTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataType
        fields = ["id", "code", "name", "is_active", "order"]


class TableCatalogSerializer(serializers.ModelSerializer):
    fields = TableFieldSerializer(many=True, read_only=True)

    class Meta:
        model = TableCatalog
        fields = [
            "id",
            "name",
            "schema",
            "description",
            "source_system",
            "owner",
            "is_active",
            "metadata",
            "last_synced_at",
            "created_at",
            "updated_at",
            "fields",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
