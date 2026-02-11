import uuid
from django.db import models
from django.conf import settings

class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80, blank=True, null=True)
    entity_id = models.CharField(max_length=80, blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
