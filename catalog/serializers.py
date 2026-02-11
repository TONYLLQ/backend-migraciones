from rest_framework import serializers
from .models import (
    ScenarioProcess, ScenarioStatus, ScenarioTransition,
    RuleDimension, ActionType,
    QualityRule, RuleAction
)

class ScenarioProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioProcess
        fields = ["id", "code", "name", "is_active", "order"]

class ScenarioStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioStatus
        fields = [
            "id", "code", "name", "is_active", "order",
            "is_terminal", "requires_all_actions_executed"
        ]

class ScenarioTransitionSerializer(serializers.ModelSerializer):
    from_status_code = serializers.CharField(source="from_status.code", read_only=True)
    to_status_code = serializers.CharField(source="to_status.code", read_only=True)

    class Meta:
        model = ScenarioTransition
        fields = [
            "id",
            "from_status", "from_status_code",
            "to_status", "to_status_code",
            "allow_coordinator", "allow_analyst", "allow_viewer",
            "is_active",
        ]

class RuleDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleDimension
        fields = ["id", "code", "name", "is_active", "order"]

class ActionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionType
        fields = ["id", "code", "name", "is_active", "order"]

class RuleActionSerializer(serializers.ModelSerializer):
    action_type_code = serializers.CharField(source="action_type.code", read_only=True)
    action_type_name = serializers.CharField(source="action_type.name", read_only=True)

    class Meta:
        model = RuleAction
        fields = ["id", "action_type", "action_type_code", "action_type_name", "description"]
        read_only_fields = ["id", "action_type_code", "action_type_name"]

class QualityRuleSerializer(serializers.ModelSerializer):
    actions = RuleActionSerializer(many=True, read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    dimension_code = serializers.CharField(source="dimension.code", read_only=True)
    dimension_name = serializers.CharField(source="dimension.name", read_only=True)

    class Meta:
        model = QualityRule
        fields = [
            "id", "name", "dimension", "dimension_code", "dimension_name",
            "is_active", "sql_query",
            "created_by", "created_by_email", "created_at", "actions"
        ]
        read_only_fields = ["id", "created_at", "created_by_email", "dimension_code", "dimension_name"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
