from django.contrib import admin

from .models import ExecutionStatus, RuleExecution, RuleExecutionLog


@admin.register(ExecutionStatus)
class ExecutionStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("order", "name")


@admin.register(RuleExecution)
class RuleExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "rule", "scenario", "status", "requested_by", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "rule__name", "scenario__title", "requested_by__email")
    ordering = ("-created_at",)


@admin.register(RuleExecutionLog)
class RuleExecutionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "execution", "level", "created_at")
    list_filter = ("level",)
    search_fields = ("execution__id", "message")
    ordering = ("-created_at",)
