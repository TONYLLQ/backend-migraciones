from rest_framework import permissions

class IsCoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "COORDINATOR")

class IsCoordinatorOrAnalyst(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ("COORDINATOR", "ANALYST"))

class ReadOnlyForViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == "VIEWER":
            return request.method in permissions.SAFE_METHODS
        return True
