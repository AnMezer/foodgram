from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()


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
