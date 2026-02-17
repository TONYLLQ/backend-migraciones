import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# --------- Catálogos escenario ----------
class ScenarioProcess(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class ScenarioStatus(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    is_terminal = models.BooleanField(default=False)
    requires_all_actions_executed = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class ScenarioTransition(models.Model):
    from_status = models.ForeignKey(ScenarioStatus, on_delete=models.CASCADE, related_name="transitions_from")
    to_status = models.ForeignKey(ScenarioStatus, on_delete=models.CASCADE, related_name="transitions_to")

    allow_coordinator = models.BooleanField(default=True)
    allow_analyst = models.BooleanField(default=False)
    allow_viewer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("from_status", "to_status")

    def __str__(self):
        return f"{self.from_status.code} -> {self.to_status.code}"

# --------- Catálogos reglas ----------
class RuleDimension(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class ActionType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class QualityRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    dimension = models.ForeignKey(RuleDimension, on_delete=models.PROTECT, related_name="quality_rules")
    is_active = models.BooleanField(default=False)
    sql_query = models.TextField(blank=True, null=True)
    sql_query_consistent = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_quality_rules",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def __str__(self):
        return f"{self.name} ({self.dimension.name if self.dimension else '-'})"

class RuleAction(models.Model):
    id = models.BigAutoField(primary_key=True)
    rule = models.ForeignKey(QualityRule, on_delete=models.CASCADE, related_name="actions")
    action_type = models.ForeignKey(ActionType, on_delete=models.PROTECT, related_name="rule_actions")
    description = models.TextField()

    def __str__(self):
        return f"{self.rule.name} - {self.action_type.name if self.action_type else '-'}"
