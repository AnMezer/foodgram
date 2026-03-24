from symtable import Class

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer

from api.filters import IngredientFilter
from api.serializers import UserCreateSerializer, UsersListSerializer, \
    AvatarEditSerializer, IdNameSlugSerializer, IngredientSerializer
from recipes.models.models import Tag, Ingredient

User = get_user_model()





class UsersViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return UserCreateSerializer
            case 'set_password':
                return SetPasswordSerializer
            case 'me':
                return UsersListSerializer
            case 'avatar':
                return AvatarEditSerializer
            case _:
                return UsersListSerializer

    def get_permissions(self):
        if self.action in ['me', 'set_password', 'avatar']:
            return (IsAuthenticated(),)
        return (AllowAny(),)

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

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
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
                user.avatar.delete()
                user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    queryset = Tag.objects.all()
    serializer_class = IdNameSlugSerializer
    permission_classes = (AllowAny,)

class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientFilter # TODO: Проверить на Postgres
    ordering = ('name',)