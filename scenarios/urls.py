from rest_framework.routers import DefaultRouter
from .views import ScenarioViewSet, ScenarioOperationalActionViewSet

router = DefaultRouter()
router.register(r"scenarios", ScenarioViewSet, basename="scenarios")
router.register(r"scenario-actions", ScenarioOperationalActionViewSet, basename="scenario-actions")

urlpatterns = router.urls
