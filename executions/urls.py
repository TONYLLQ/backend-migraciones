from rest_framework.routers import DefaultRouter

from .views import ExecutionStatusViewSet, RuleExecutionViewSet, RuleExecutionLogViewSet

router = DefaultRouter()
router.register(r"statuses", ExecutionStatusViewSet, basename="execution-status")
router.register(r"executions", RuleExecutionViewSet, basename="rule-execution")
router.register(r"execution-logs", RuleExecutionLogViewSet, basename="rule-execution-log")

urlpatterns = router.urls
