import uuid
from django.db import models
from django.conf import settings

from catalog.models import QualityRule
from scenarios.models import Scenario


class ExecutionStatus(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class RuleExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(QualityRule, on_delete=models.PROTECT, related_name="executions")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="executions")
    status = models.ForeignKey(ExecutionStatus, on_delete=models.PROTECT, related_name="rule_executions")

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rule_executions_requested",
    )

    sql_snapshot = models.TextField(blank=True, null=True)
    rows_affected = models.IntegerField(blank=True, null=True)
    result_sample = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rule.name} - {self.status.code}"


class RuleExecutionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    execution = models.ForeignKey(RuleExecution, on_delete=models.CASCADE, related_name="logs")
    level = models.CharField(max_length=20, default="INFO")
    message = models.TextField()
    payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.execution_id} - {self.level}"
