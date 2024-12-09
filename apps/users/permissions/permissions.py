from rest_framework.permissions import BasePermission


class IsExecutor(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'studio_profile') or hasattr(request.user, 'photographer_profile'):
            return True

        return False


class IsClient(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'studio_profile'):
            return True

        return False


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.base_user == request.user

