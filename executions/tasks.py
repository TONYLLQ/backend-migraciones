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

def _strip_trailing_order_by(sql: str) -> str:
    lower = sql.lower()
    depth = 0
    last_order_by = -1
    i = 0
    while i < len(sql) - 7:
        ch = sql[i]
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        if depth == 0 and lower.startswith("order by", i):
            prev_ok = i == 0 or not lower[i - 1].isalnum()
            if prev_ok:
                last_order_by = i
        i += 1
    if last_order_by != -1:
        return sql[:last_order_by].rstrip()
    return sql


@shared_task
def execute_rule(execution_id: str, mode: str = "inconsistent"):
    execution = RuleExecution.objects.select_related("rule").get(id=execution_id)

    running = _get_status("RUNNING")
    success = _get_status("SUCCESS")
    failed = _get_status("FAILED")

    execution.status = running or execution.status
    execution.started_at = timezone.now()
    execution.save(update_fields=["status", "started_at"])

    if (mode or "").lower() == "consistent":
        sql = (execution.rule.sql_query_consistent or "").strip()
    else:
        sql = (execution.rule.sql_query or "").strip()

    if not sql:
        execution.status = failed or execution.status
        execution.error_message = "No hay SQL configurado para ejecutar."
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
        return

    sql = sql.rstrip().rstrip(";")
    execution.sql_snapshot = sql
    execution.execution_mode = (mode or "inconsistent").lower()
    execution.save(update_fields=["sql_snapshot", "execution_mode"])

    if not sql.lower().startswith("select"):
        execution.status = failed or execution.status
        execution.error_message = "Solo se permite ejecutar consultas SELECT."
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
        return

    try:
        # Use external SQL Server for heavy queries
        with connections["mssql"].cursor() as cursor:
            if (mode or "").lower() == "consistent":
                sql_base = _strip_trailing_order_by(sql)
                # Full count without loading all rows
                count_sql = f"SELECT COUNT(*) FROM ({sql_base}) AS subq"
                cursor.execute(count_sql)
                total_rows = cursor.fetchone()[0]

                # Sample only first 100 rows
                sample_sql = f"SELECT TOP 100 * FROM ({sql_base}) AS subq"
                cursor.execute(sample_sql)
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

                execution.rows_affected = total_rows
                safe_rows = [_json_safe_row(row) for row in rows]
                execution.result_sample = {"columns": columns, "rows": safe_rows, "sample_size": len(rows)}
            else:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

                execution.rows_affected = len(rows)
                safe_rows = [_json_safe_row(row) for row in rows]
                execution.result_sample = {"columns": columns, "rows": safe_rows}

        execution.status = success or execution.status
        execution.finished_at = timezone.now()
        execution.save(update_fields=["execution_mode", "rows_affected", "result_sample", "status", "finished_at"])
        
    except Exception as exc:
        execution.status = failed or execution.status
        execution.error_message = str(exc)
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
