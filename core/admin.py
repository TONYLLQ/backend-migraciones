from django.contrib import admin
from .models import AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event", "actor", "entity_type", "entity_id", "created_at")
    list_filter = ("event", "entity_type")
    search_fields = ("event", "entity_id", "actor__email")
