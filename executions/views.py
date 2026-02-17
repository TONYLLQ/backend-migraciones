from django.db import transaction
from django.db.models import OuterRef, Subquery, IntegerField, Sum, Count
from django.db.models.functions import Coalesce
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
from catalog.models import QualityRule


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
        mode = (request.data.get("mode") or "inconsistent").lower()

        if not rule_id or not scenario_id:
            return Response(
                {"detail": "rule y scenario son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if mode not in ("inconsistent", "consistent"):
            return Response(
                {"detail": "mode invalido. Use 'inconsistent' o 'consistent'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending = ExecutionStatus.objects.filter(code="PENDING").first()
        execution = RuleExecution.objects.create(
            rule_id=rule_id,
            scenario_id=scenario_id,
            status=pending,
            requested_by=request.user,
            execution_mode=mode,
        )

        transaction.on_commit(lambda: execute_rule.delay(str(execution.id), mode))
        serializer = self.get_serializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="observed-rules-count")
    def observed_rules_count(self, request):
        latest_exec = RuleExecution.objects.filter(
            rule_id=OuterRef("pk")
        ).order_by("-created_at")
        observed = QualityRule.objects.annotate(
            latest_rows=Subquery(
                latest_exec.values("rows_affected")[:1],
                output_field=IntegerField(),
            )
        ).filter(latest_rows__gte=1)
        observed_count = observed.count()
        observed_sum = observed.aggregate(total=Sum("latest_rows"))["total"] or 0
        return Response({"count": observed_count, "total_rows": observed_sum})

    @action(detail=False, methods=["get"], url_path="observed-rules-by-dimension")
    def observed_rules_by_dimension(self, request):
        latest_exec = RuleExecution.objects.filter(
            rule_id=OuterRef("pk")
        ).order_by("-created_at")
        observed = QualityRule.objects.annotate(
            latest_rows=Subquery(
                latest_exec.values("rows_affected")[:1],
                output_field=IntegerField(),
            )
        ).filter(latest_rows__gte=1)
        data = (
            observed.values("dimension__id", "dimension__code", "dimension__name")
            .annotate(count=Count("id"))
            .order_by("dimension__name")
        )
        return Response(list(data))

    @action(detail=False, methods=["get"], url_path="quality-rate")
    def quality_rate(self, request):
        latest_inconsistent = RuleExecution.objects.filter(
            rule_id=OuterRef("pk"),
            execution_mode="inconsistent",
        ).order_by("-created_at")
        latest_consistent = RuleExecution.objects.filter(
            rule_id=OuterRef("pk"),
            execution_mode="consistent",
        ).order_by("-created_at")

        rules = QualityRule.objects.annotate(
            inconsistent_rows=Subquery(
                latest_inconsistent.values("rows_affected")[:1],
                output_field=IntegerField(),
            ),
            consistent_rows=Subquery(
                latest_consistent.values("rows_affected")[:1],
                output_field=IntegerField(),
            ),
        )

        totals = rules.aggregate(
            inconsistent=Sum(Coalesce("inconsistent_rows", 0)),
            consistent=Sum(Coalesce("consistent_rows", 0)),
        )
        inconsistent = totals["inconsistent"] or 0
        consistent = totals["consistent"] or 0
        denom = inconsistent + consistent
        rate = None if denom == 0 else (1 - (inconsistent / denom)) * 100

        return Response({
            "inconsistent": inconsistent,
            "consistent": consistent,
            "rate": rate,
        })


class RuleExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleExecutionLog.objects.all()
    serializer_class = RuleExecutionLogSerializer
    permission_classes = [IsAuthenticated]
