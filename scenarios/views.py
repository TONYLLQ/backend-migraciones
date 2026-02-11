from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from accounts.permissions import ReadOnlyForViewer
from .models import Scenario, ScenarioOperationalAction, ScenarioHistory, OperationalActionStatus
from .serializers import (
    ScenarioSerializer,
    ScenarioOperationalActionSerializer,
    ScenarioTransitionRequestSerializer,
    OperationalActionStatusSerializer,
)
from .transitions import can_transition

class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer]

    def get_queryset(self):
        qs = Scenario.objects.select_related(
            "process", "status", "analyst", "created_by"
        ).prefetch_related(
            "rules", "operational_actions", "history"
        )

        user = self.request.user
        if user.role == "ANALYST":
            qs = qs.filter(analyst=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
