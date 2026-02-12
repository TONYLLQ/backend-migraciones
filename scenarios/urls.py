from rest_framework.routers import DefaultRouter
from .views import ScenarioViewSet, ScenarioOperationalActionViewSet, ScenarioRuleViewSet

router = DefaultRouter()
router.register(r"scenarios", ScenarioViewSet, basename="scenarios")
router.register(r"scenario-actions", ScenarioOperationalActionViewSet, basename="scenario-actions")
router.register(r"scenario-rules", ScenarioRuleViewSet, basename="scenario-rules")

urlpatterns = router.urls
