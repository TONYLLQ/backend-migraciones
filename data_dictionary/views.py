from rest_framework import viewsets, permissions
from accounts.permissions import ReadOnlyForViewer, IsCoordinatorOrAnalyst
from .models import TableCatalog, TableField, DataType
from .serializers import TableCatalogSerializer, TableFieldSerializer, DataTypeSerializer


class TableCatalogViewSet(viewsets.ModelViewSet):
    queryset = TableCatalog.objects.all()
    serializer_class = TableCatalogSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]


class TableFieldViewSet(viewsets.ModelViewSet):
    queryset = TableField.objects.select_related("table", "data_type").all()
    serializer_class = TableFieldSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]


class DataTypeViewSet(viewsets.ModelViewSet):
    queryset = DataType.objects.all()
    serializer_class = DataTypeSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyForViewer, IsCoordinatorOrAnalyst]
