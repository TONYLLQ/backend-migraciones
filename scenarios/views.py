from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from accounts.permissions import IsCoordinator

from accounts.permissions import ReadOnlyForViewer
from .models import Scenario, ScenarioRule, ScenarioOperationalAction, ScenarioHistory, OperationalActionStatus
from catalog.models import ScenarioStatus
from .serializers import (
    ScenarioSerializer,
    ScenarioRuleSerializer,
    ScenarioOperationalActionSerializer,
    ScenarioTransitionRequestSerializer,
    OperationalActionStatusSerializer,
)
from .transitions import can_transition

class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Scenario.objects.select_related(
            "process", "status", "analyst", "created_by"
        ).prefetch_related(
            "rules", "operational_actions", "history"
        ).annotate(
            rules_count=Count("rules", distinct=True)
        )

        user = self.request.user
        if user.role == "ANALYST":
            qs = qs.filter(Q(analyst=user) | Q(created_by=user))
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(created_by=user, analyst=user if user.role == "ANALYST" else None)
        if "archive" in self.request.FILES:
            instance.archive_uploaded_at = timezone.now()
            instance.archive_stage = instance.status
            instance.save(update_fields=["archive_uploaded_at", "archive_stage"])

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        scenario = self.get_object()
        ser = ScenarioTransitionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        to_status = ser.validated_data["to_status"]
        comment = ser.validated_data.get("comment") or ""

        try:
            can_transition(request.user.role, scenario, to_status)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        scenario.status = to_status
        scenario.save(update_fields=["status"])

        ScenarioHistory.objects.create(
            scenario=scenario,
            status=to_status,
            changed_by=request.user,
            comment=comment,
        )

        return Response({"status": to_status.code, "status_name": to_status.name})

    @action(detail=True, methods=["post"], url_path="assign", permission_classes=[permissions.IsAuthenticated, IsCoordinator])
    def assign(self, request, pk=None):
        scenario = self.get_object()
        if scenario.rules.count() == 0:
            return Response(
                {"detail": "El escenario debe tener al menos una regla asociada antes de asignar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        analyst_id = request.data.get("analyst")
        if not analyst_id:
            return Response({"detail": "Analyst is required."}, status=status.HTTP_400_BAD_REQUEST)
        scenario.analyst_id = analyst_id
        scenario.save(update_fields=["analyst"])

        # Auto-advance to ASSIGNED if configured
        assigned_status = ScenarioStatus.objects.filter(code__in=["ASSIGNED", "ASIGNADO"]).first()
        if assigned_status and scenario.status_id != assigned_status.id:
            try:
                can_transition(request.user.role, scenario, assigned_status)
                scenario.status = assigned_status
                scenario.save(update_fields=["status"])
                ScenarioHistory.objects.create(
                    scenario=scenario,
                    status=assigned_status,
                    changed_by=request.user,
                    comment="Asignado a analista",
                )
            except ValidationError:
                pass

        return Response({"detail": "Analyst assigned."})

    @action(detail=True, methods=["post"], url_path="unlink-rule", permission_classes=[permissions.IsAuthenticated, ReadOnlyForViewer])
    def unlink_rule(self, request, pk=None):
        scenario = self.get_object()
        rule_id = request.data.get("rule")
        if not rule_id:
            return Response({"detail": "Rule is required."}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = ScenarioRule.objects.filter(scenario=scenario, rule_id=rule_id).delete()
        if deleted == 0:
            return Response({"detail": "Rule not linked to scenario."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Rule unlinked."})

    def perform_update(self, serializer):
        instance = serializer.save()
        if "archive" in self.request.FILES:
            instance.archive_uploaded_at = timezone.now()
            instance.archive_stage = instance.status
            instance.save(update_fields=["archive_uploaded_at", "archive_stage"])

class ScenarioOperationalActionViewSet(viewsets.ModelViewSet):
    queryset = ScenarioOperationalAction.objects.select_related("scenario", "rule", "responsible", "status").all()
    serializer_class = ScenarioOperationalActionSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == "ANALYST":
            qs = qs.filter(scenario__analyst=user)
        return qs

class OperationalActionStatusViewSet(viewsets.ModelViewSet):
    queryset = OperationalActionStatus.objects.all()
    serializer_class = OperationalActionStatusSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer]

class ScenarioRuleViewSet(viewsets.ModelViewSet):
    queryset = ScenarioRule.objects.all()
    serializer_class = ScenarioRuleSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer]
