from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter
from api.v1.serializers.serializers import IngredientSerializer
from recipes.models import Ingredient


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientFilter
    ordering = ('name',)
    permission_classes = (AllowAny,)
    pagination_class = None
    authentication_classes = ()
