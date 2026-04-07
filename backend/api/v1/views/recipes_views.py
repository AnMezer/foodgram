# flake8: noqa: E999
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site

from api.filters import RecipeFilter
from recipes.models import Favorite, ShoppingCart
from api.v1.serializers.serializers import (
    RecipeSerializer, RecipeShortSerializer, RecipeReadSerializer)
from api.utils import decode_id, encode_id, get_shopping_list
from recipes.models import Recipe
from recipes.permissions import IsAuthorOrReadonly


def redirect_to_recipe(request, hashed_id):
    """Перенаправляет с короткой ссылки на страницу рецепта"""
    recipe_pk = decode_id(hashed_id)
    domain = get_current_site(request)
    if not recipe_pk or not Recipe.objects.filter(pk=recipe_pk).exists():
        redirect_url = domain
    else:
        redirect_url = f'{domain}/recipes/{recipe_pk}'
    return redirect(redirect_url)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-created_at',)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadonly)

    def get_queryset(self):
        match self.action:
            case 'list' | 'retrieve':
                return (Recipe.objects.all()
                        .select_related('author')
                        .prefetch_related('tags',
                                          'ingredients',
                                          'recipe_ingredients__ingredient'))
            case _:
                return Recipe.objects.all()

    def get_authenticators(self):
        authenticators = super().get_authenticators()
        if hasattr(self, 'action'):
            match self.action:
                case 'list' | 'retrieve' | 'get_link':
                    return ()
                case _:
                    return authenticators
        return authenticators

    def get_serializer_class(self):
        match self.action:
            case 'favorite' | 'shopping_cart':
                return RecipeShortSerializer
            case 'list' | 'retrieve':
                return RecipeReadSerializer
            case _:
                return RecipeSerializer

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk):
        encoded_id = encode_id(int(pk))
        short_link = request.build_absolute_uri(f'/s/{encoded_id}')
        return Response({'short-link': short_link})

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        return self.toggle_recipe(Favorite, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        return self.toggle_recipe(Favorite, pk)

    @action(detail=True, methods=['POST'])
    def shopping_cart(self, request, pk):
        return self.toggle_recipe(ShoppingCart, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, requers, pk):
        return self.toggle_recipe(ShoppingCart, pk)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        return get_shopping_list(request.user)

    def toggle_recipe(self, model, pk):
        """Добавляет/удаляет рецепт в избранное, корзину покупок"""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        instance = model.objects.filter(user=user, recipe=recipe)

        if self.request.method == 'POST':
            if instance.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            model.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe,
                                             context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            deleted, _ = (model.objects
                          .filter(user=self.request.user, recipe=pk)
                          .delete())
            if not deleted:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
