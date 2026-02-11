from django.contrib import admin
from .models import (
    ScenarioProcess, ScenarioStatus, ScenarioTransition,
    RuleDimension, ActionType,
    QualityRule, RuleAction
)

@admin.register(ScenarioProcess)
class ScenarioProcessAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("order", "name")

@admin.register(ScenarioStatus)
class ScenarioStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order", "is_terminal", "requires_all_actions_executed")
    list_filter = ("is_active", "is_terminal")
    search_fields = ("code", "name")
    ordering = ("order", "name")

@admin.register(ScenarioTransition)
class ScenarioTransitionAdmin(admin.ModelAdmin):
    list_display = ("from_status", "to_status", "is_active", "allow_coordinator", "allow_analyst", "allow_viewer")
    list_filter = ("is_active", "allow_coordinator", "allow_analyst", "allow_viewer")
    search_fields = ("from_status__code", "to_status__code")

class RuleActionInline(admin.TabularInline):
    model = RuleAction
    extra = 1

@admin.register(QualityRule)
class QualityRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "dimension", "is_active", "created_by", "created_at")
    list_filter = ("dimension", "is_active")
    search_fields = ("name", "sql_query")
    inlines = [RuleActionInline]

@admin.register(RuleAction)
class RuleActionAdmin(admin.ModelAdmin):
    list_display = ("rule", "action_type")
    list_filter = ("action_type",)
    search_fields = ("rule__name", "description")

@admin.register(RuleDimension)
class RuleDimensionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("order", "name")

@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("order", "name")
