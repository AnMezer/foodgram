import django_filters

from api.utils import get_bool
from recipes.models import Tag
from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                                    to_field_name='slug',
                                                    queryset=Tag.objects.all())
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if (request
                and value
                and get_bool(value)
                and request.user.is_authenticated):
            return queryset.filter(shoppingcart__user=request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if (request
                and value
                and get_bool(value)
                and request.user.is_authenticated):
            return queryset.filter(favorite__user=request.user)
        return queryset
