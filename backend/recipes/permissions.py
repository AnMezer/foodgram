from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, BasePermission, \
    SAFE_METHODS

User = get_user_model()

# TODO: удалить лишнее
class IsOwner(IsAuthenticated):
    """Разрешает доступ только владельцу объекта"""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsOwnerOrAdmin(IsOwner):
    """Разрешает доступ владельцу объекта или администратору"""
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or super().has_object_permission(
            request, view, obj)


class IsSelfUser(IsAuthenticated):
    """Разрешает пользователю доступ только к своим данным"""
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsAuthorOrReadonly(BasePermission):
    """Разрешает безопасные методы всем пользователям,
    небезопасные только владельцу объекта или администратору"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (request.user.is_authenticated
                and (request.user.is_superuser
                     or getattr(obj, 'author', None) == request.user
                     or obj == request.user))