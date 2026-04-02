from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


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
