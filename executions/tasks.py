from datetime import date, datetime, time
from decimal import Decimal
import uuid

from celery import shared_task
from django.db import connections
from django.utils import timezone

from .models import ExecutionStatus, RuleExecution


def _get_status(code: str):
    return ExecutionStatus.objects.filter(code=code).first()

def _json_safe(value):
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        value = timezone.localtime(value, timezone.get_current_timezone())
        return value.isoformat()
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    return value

def _json_safe_row(row):
    return [_json_safe(v) for v in row]


@shared_task
def execute_rule(execution_id: str):
    execution = RuleExecution.objects.select_related("rule").get(id=execution_id)

    running = _get_status("RUNNING")
    success = _get_status("SUCCESS")
    failed = _get_status("FAILED")

    execution.status = running or execution.status
    execution.started_at = timezone.now()
    execution.save(update_fields=["status", "started_at"])

    sql = (execution.rule.sql_query or "").strip()
    execution.sql_snapshot = sql
    execution.save(update_fields=["sql_snapshot"])

    if not sql.lower().startswith("select"):
        execution.status = failed or execution.status
        execution.error_message = "Solo se permite ejecutar consultas SELECT."
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
        return

    try:
        # Use external SQL Server for heavy queries
        with connections["mssql"].cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

        execution.rows_affected = len(rows)
        safe_rows = [_json_safe_row(row) for row in rows]
        execution.result_sample = {"columns": columns, "rows": safe_rows}
        execution.status = success or execution.status
        execution.finished_at = timezone.now()
        execution.save(update_fields=["rows_affected", "result_sample", "status", "finished_at"])
        
    except Exception as exc:
        execution.status = failed or execution.status
        execution.error_message = str(exc)
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
