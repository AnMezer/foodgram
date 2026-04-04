from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.models import Favorite, ShoppingCart
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             RecipeShortSerializer, TagSerializer)
from api.utils import decode_id, encode_id
from project_settings import config
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.permissions import IsOwnerOrAdmin
from recipes.v1.viewsets import ListRetrieveBaseModel


def redirect_to_recipe(request, hashed_id):
    """Перенаправляет с короткой ссылки на страницу рецепта"""
    recipe_pk = decode_id(hashed_id)
    if not recipe_pk or not Recipe.objects.filter(pk=recipe_pk).exists():
        redirect_url = f'{config.FRONTEND_URL}'
    else:
        redirect_url = f'{config.FRONTEND_URL}/recipes/ {recipe_pk}'
    return redirect(redirect_url)


class TagsViewSet(ListRetrieveBaseModel):
    """Вьюсет для тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ListRetrieveBaseModel):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientFilter
    ordering = ('name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-created_at',)

    def get_permissions(self):
        match self.action:
            case ('create'
                  | 'shopping_cart'
                  | 'download_shopping_cart'
                  | 'favorite'):
                return (IsAuthenticated(),)
            case ('update'
                  | 'partial_update'
                  | 'destroy'):
                return (IsOwnerOrAdmin(),)
            case _:
                return (AllowAny(),)

    def get_serializer_class(self):
        match self.action:
            case 'favorite' | 'shopping_cart':
                return RecipeShortSerializer
            case _:
                return RecipeSerializer

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk):
        encoded_id = encode_id(int(pk))
        short_link = request.build_absolute_uri(f'/s/{encoded_id}')
        return Response({'short-link': short_link})

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk):
        return self.toggle_recipe(Favorite, pk)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        return self.toggle_recipe(ShoppingCart, pk)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = (RecipeIngredient.objects
                       .filter(recipe__shoppingcart__user=request.user)
                       .values('ingredient__name',
                               'ingredient__measurement_unit')
                       .annotate(total_amount=Sum('amount')))

        shopping_list = ['СПИСОК ПОКУПОК:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['total_amount']
            meas_unit = ingredient['ingredient__measurement_unit']
            shopping_list.append(f'{" " * 4}-- {name}: {amount} {meas_unit}')
        result = '\n'.join(shopping_list)

        response = HttpResponse(result,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response

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
            if not instance.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
