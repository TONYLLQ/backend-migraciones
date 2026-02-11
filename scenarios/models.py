import uuid
from django.db import models
from django.conf import settings
from catalog.models import QualityRule, ScenarioProcess, ScenarioStatus

class OperationalActionStatus(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class Scenario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    process = models.ForeignKey(ScenarioProcess, on_delete=models.PROTECT, related_name="scenarios")
    status = models.ForeignKey(ScenarioStatus, on_delete=models.PROTECT, related_name="scenarios")

    analyst = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_scenarios",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_scenarios",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    rules = models.ManyToManyField(QualityRule, through="ScenarioRule", related_name="scenarios")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.status.code}]"

class ScenarioRule(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    rule = models.ForeignKey(QualityRule, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("scenario", "rule")

class ScenarioOperationalAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="operational_actions")
    rule = models.ForeignKey(QualityRule, on_delete=models.PROTECT, related_name="operational_actions")

    description = models.TextField()
    status = models.ForeignKey(OperationalActionStatus, on_delete=models.PROTECT, related_name="operational_actions")

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="responsible_actions",
    )

    evidence_url = models.TextField(blank=True, null=True)
    correction_query = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class ScenarioHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="history")
    status = models.ForeignKey(ScenarioStatus, on_delete=models.PROTECT)

    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="scenario_changes",
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-changed_at"]
