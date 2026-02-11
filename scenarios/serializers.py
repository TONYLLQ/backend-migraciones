from rest_framework import serializers
from catalog.models import QualityRule, ScenarioStatus
from .models import (
    OperationalActionStatus,
    Scenario,
    ScenarioOperationalAction,
    ScenarioHistory,
)

class ScenarioHistorySerializer(serializers.ModelSerializer):
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = ScenarioHistory
        fields = ["id", "status", "status_code", "status_name", "changed_at", "changed_by", "changed_by_email", "comment"]
        read_only_fields = ["id", "changed_at", "status_code", "status_name", "changed_by_email"]

class ScenarioOperationalActionSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    responsible_email = serializers.CharField(source="responsible.email", read_only=True)
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = ScenarioOperationalAction
        fields = [
            "id", "scenario", "rule", "rule_name",
            "description", "status", "status_code", "status_name",
            "responsible", "responsible_email",
            "evidence_url", "correction_query",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "rule_name", "responsible_email", "status_code", "status_name"]

class ScenarioSerializer(serializers.ModelSerializer):
    process_code = serializers.CharField(source="process.code", read_only=True)
    process_name = serializers.CharField(source="process.name", read_only=True)
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    rules = serializers.PrimaryKeyRelatedField(many=True, queryset=QualityRule.objects.all(), required=False)
    operational_actions = ScenarioOperationalActionSerializer(many=True, read_only=True)
    history = ScenarioHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Scenario
        fields = [
            "id", "title",
            "process", "process_code", "process_name",
            "status", "status_code", "status_name",
            "analyst", "created_by", "created_at",
            "rules", "operational_actions", "history",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    def create(self, validated_data):
        request = self.context["request"]
        rules = validated_data.pop("rules", [])
        validated_data["created_by"] = request.user

        scenario = super().create(validated_data)

        if rules:
            scenario.rules.set(rules)

        ScenarioHistory.objects.create(
            scenario=scenario,
            status=scenario.status,
            changed_by=request.user,
            comment="Escenario creado",
        )
        return scenario

class ScenarioTransitionRequestSerializer(serializers.Serializer):
    to_status = serializers.PrimaryKeyRelatedField(queryset=ScenarioStatus.objects.all())
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class OperationalActionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalActionStatus
        fields = ["id", "code", "name", "is_active", "order"]
