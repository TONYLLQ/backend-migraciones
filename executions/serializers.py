from rest_framework import serializers

from .models import ExecutionStatus

from .models import ExecutionStatus, RuleExecution, RuleExecutionLog


class ExecutionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionStatus
        fields = ["id", "code", "name", "is_active", "order"]


class RuleExecutionSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=ExecutionStatus.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = RuleExecution
        fields = [
            "id",
            "rule",
            "scenario",
            "status",
            "requested_by",
            "sql_snapshot",
            "rows_affected",
            "result_sample",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        if not validated_data.get("status"):
            validated_data["status"] = ExecutionStatus.objects.filter(code="PENDING").first()
        return super().create(validated_data)


class RuleExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleExecutionLog
        fields = ["id", "execution", "level", "message", "payload", "created_at"]
        read_only_fields = ["created_at"]
