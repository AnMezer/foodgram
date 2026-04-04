# flake8: noqa: E999
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (AvatarEditSerializer, SetPasswordSerializer,
                             SubscribeSerializer, UserCreateSerializer,
                             UsersListSerializer)
from recipes.permissions import IsSelfUser
from users.models import Subscribe

User = get_user_model()


class UsersViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для пользователей"""
    lookup_field = 'pk'
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return UserCreateSerializer
            case 'retrieve' | 'me':
                return UsersListSerializer
            case 'set_password':
                return SetPasswordSerializer
            case 'avatar':
                return AvatarEditSerializer
            case 'subscribe' | 'subscriptions':
                return SubscribeSerializer
            case _:
                return UsersListSerializer

    def get_permissions(self):
        match self.action:
            case 'me' | 'set_password' | 'avatar':
                return (IsSelfUser(),)
            case 'subscribe':
                return (IsAuthenticated(),)
            case 'create' | 'list' | 'retrieve':
                return (AllowAny(),)
            case _:
                return (IsAuthenticated(),)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = self.get_serializer(request.user,
                                         context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['PUT', 'DELETE'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = self.get_serializer(user,
                                             data=request.data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar = None
                user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        is_subscription_exists = Subscribe.objects.filter(
            user_id=pk, subscriber=user).exists()
        if request.method == 'POST':
            if is_subscription_exists or int(pk) == user.id:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(subscriber=user, user=author)
            serializer = self.get_serializer(author,
                                             context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not is_subscription_exists:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset = Subscribe.objects.filter(user=author, subscriber=user)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribe__subscriber=self.request.user)
        queryset_paginated = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset_paginated, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
