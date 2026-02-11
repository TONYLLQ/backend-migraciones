from django.contrib import admin
from .models import Scenario, ScenarioRule, ScenarioOperationalAction, ScenarioHistory, OperationalActionStatus

class ScenarioRuleInline(admin.TabularInline):
    model = ScenarioRule
    extra = 1

class ScenarioOperationalActionInline(admin.TabularInline):
    model = ScenarioOperationalAction
    extra = 0

class ScenarioHistoryInline(admin.TabularInline):
    model = ScenarioHistory
    extra = 0
    readonly_fields = ("changed_at",)

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("title", "process", "status", "analyst", "created_by", "created_at")
    list_filter = ("process", "status")
    search_fields = ("title",)
    ordering = ("-created_at",)
    inlines = [ScenarioRuleInline, ScenarioOperationalActionInline, ScenarioHistoryInline]

@admin.register(ScenarioOperationalAction)
class ScenarioOperationalActionAdmin(admin.ModelAdmin):
    list_display = ("id", "scenario", "rule", "status", "responsible", "created_at")
    list_filter = ("status",)
    search_fields = ("description", "scenario__title", "rule__name")

@admin.register(ScenarioHistory)
class ScenarioHistoryAdmin(admin.ModelAdmin):
    list_display = ("scenario", "status", "changed_by", "changed_at")
    list_filter = ("status",)
    search_fields = ("scenario__title", "comment")


@admin.register(OperationalActionStatus)
class OperationalActionStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("order", "name")
