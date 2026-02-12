from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .permissions import IsCoordinator
from .models import UserRole

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="analysts")
    def analysts(self, request):
        queryset = User.objects.filter(role=UserRole.ANALYST, is_active=True).order_by("first_name", "last_name", "email")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
