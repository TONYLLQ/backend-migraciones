from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ExecutionStatus, RuleExecution, RuleExecutionLog
from .serializers import (
    ExecutionStatusSerializer,
    RuleExecutionSerializer,
    RuleExecutionLogSerializer,
)
from .tasks import execute_rule


class ExecutionStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExecutionStatus.objects.all()
    serializer_class = ExecutionStatusSerializer
    permission_classes = [IsAuthenticated]


class RuleExecutionViewSet(viewsets.ModelViewSet):
    queryset = RuleExecution.objects.all()
    serializer_class = RuleExecutionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="execute")
    def execute(self, request):
        rule_id = request.data.get("rule")
        scenario_id = request.data.get("scenario")

        if not rule_id or not scenario_id:
            return Response(
                {"detail": "rule y scenario son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending = ExecutionStatus.objects.filter(code="PENDING").first()
        execution = RuleExecution.objects.create(
            rule_id=rule_id,
            scenario_id=scenario_id,
            status=pending,
            requested_by=request.user,
        )

        execute_rule.delay(str(execution.id))
        serializer = self.get_serializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RuleExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleExecutionLog.objects.all()
    serializer_class = RuleExecutionLogSerializer
    permission_classes = [IsAuthenticated]
