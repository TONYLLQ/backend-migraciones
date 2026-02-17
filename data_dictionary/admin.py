from django.contrib import admin
from .models import TableCatalog, TableField, DataType


@admin.register(TableCatalog)
class TableCatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "schema", "source_system", "owner", "is_active", "last_synced_at")
    search_fields = ("name", "schema", "source_system", "owner")


@admin.register(TableField)
class TableFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "table", "data_type", "analysis_required", "is_primary_key", "is_foreign_key")
    list_filter = ("analysis_required", "is_primary_key", "is_foreign_key", "is_nullable")
    search_fields = ("name", "table__name")


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
