import django_filters

from api.utils import get_bool
from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):

    author = django_filters.NumberFilter(field_name='author_id')
    tags = django_filters.CharFilter(method='filter_tags')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_tags(self, queryset, name, value):
        request = self.request
        if not request:
            return queryset
        tags = request.query_params.getlist('tags')
        tags = [tag for tag in tags if tag]
        if tags:
            return queryset.filter(tags__slug__in=tags)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if (request
                and value
                and get_bool(value)
                and self.request.user.is_authenticated):
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if (request
                and value
                and get_bool(value)
                and self.request.user.is_authenticated):
            return queryset.filter(favorite__user=self.request.user)
        return queryset
