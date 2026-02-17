from rest_framework.routers import DefaultRouter
from .views import TableCatalogViewSet, TableFieldViewSet, DataTypeViewSet

router = DefaultRouter()
router.register(r"tables", TableCatalogViewSet, basename="data-dictionary-tables")
router.register(r"fields", TableFieldViewSet, basename="data-dictionary-fields")
router.register(r"data-types", DataTypeViewSet, basename="data-dictionary-data-types")

urlpatterns = router.urls
