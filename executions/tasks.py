from celery import shared_task
from django.db import connection, transaction
from django.utils import timezone

from .models import ExecutionStatus, RuleExecution


def _get_status(code: str):
    return ExecutionStatus.objects.filter(code=code).first()


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
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(50)

        execution.rows_affected = len(rows)
        execution.result_sample = {"columns": columns, "rows": rows}
        execution.status = success or execution.status
        execution.finished_at = timezone.now()
        execution.save(update_fields=["rows_affected", "result_sample", "status", "finished_at"])
    except Exception as exc:
        execution.status = failed or execution.status
        execution.error_message = str(exc)
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "error_message", "finished_at"])
