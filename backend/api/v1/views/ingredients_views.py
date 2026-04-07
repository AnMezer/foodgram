from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from api.filters import IngredientFilter
from api.v1.serializers.serializers import IngredientSerializer
from api.v1.views.viewsets import ListRetrieveBaseModel
from recipes.models import Ingredient


class IngredientsViewSet(ListRetrieveBaseModel):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientFilter
    ordering = ('name',)
