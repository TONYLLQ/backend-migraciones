from rest_framework import viewsets, permissions
from accounts.permissions import ReadOnlyForViewer, IsCoordinatorOrAnalyst
from .models import (
    ScenarioProcess, ScenarioStatus, ScenarioTransition,
    RuleDimension, ActionType,
    QualityRule, RuleAction
)
from .serializers import (
    ScenarioProcessSerializer, ScenarioStatusSerializer, ScenarioTransitionSerializer,
    RuleDimensionSerializer, ActionTypeSerializer,
    QualityRuleSerializer, RuleActionSerializer
)

class ScenarioProcessViewSet(viewsets.ModelViewSet):
    queryset = ScenarioProcess.objects.all()
    serializer_class = ScenarioProcessSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class ScenarioStatusViewSet(viewsets.ModelViewSet):
    queryset = ScenarioStatus.objects.all()
    serializer_class = ScenarioStatusSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class ScenarioTransitionViewSet(viewsets.ModelViewSet):
    queryset = ScenarioTransition.objects.select_related("from_status", "to_status").all()
    serializer_class = ScenarioTransitionSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class QualityRuleViewSet(viewsets.ModelViewSet):
    queryset = QualityRule.objects.select_related("dimension", "created_by").prefetch_related("actions").all()
    serializer_class = QualityRuleSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class RuleActionViewSet(viewsets.ModelViewSet):
    queryset = RuleAction.objects.select_related("rule", "action_type").all()
    serializer_class = RuleActionSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class RuleDimensionViewSet(viewsets.ModelViewSet):
    queryset = RuleDimension.objects.all()
    serializer_class = RuleDimensionSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]

class ActionTypeViewSet(viewsets.ModelViewSet):
    queryset = ActionType.objects.all()
    serializer_class = ActionTypeSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]
