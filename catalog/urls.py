from rest_framework.routers import DefaultRouter
from .views import (
    ScenarioProcessViewSet, ScenarioStatusViewSet, ScenarioTransitionViewSet,
    RuleDimensionViewSet, ActionTypeViewSet,
    QualityRuleViewSet, RuleActionViewSet
)

router = DefaultRouter()
router.register(r"scenario-processes", ScenarioProcessViewSet, basename="scenario-processes")
router.register(r"scenario-statuses", ScenarioStatusViewSet, basename="scenario-statuses")
router.register(r"scenario-transitions", ScenarioTransitionViewSet, basename="scenario-transitions")
router.register(r"quality-rules", QualityRuleViewSet, basename="quality-rules")
router.register(r"rule-actions", RuleActionViewSet, basename="rule-actions")
router.register(r"rule-dimensions", RuleDimensionViewSet, basename="rule-dimensions")
router.register(r"action-types", ActionTypeViewSet, basename="action-types")

urlpatterns = router.urls
