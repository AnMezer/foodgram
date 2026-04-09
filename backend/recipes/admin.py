from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import Favorite, ShoppingCart
from .models.ingredient import Ingredient
from .models.recipe import Recipe
from .models.recipe_ingredient import RecipeIngredient
from .models.tag import Tag

User = get_user_model()


def get_ingredients_list(ingredients):
    if ingredients.exists():
        ingredients_list = [
            (f'<li>{item.ingredient.name} - ({item.amount}'
             f'{item.ingredient.measurement_unit})</li>')
            for item in ingredients
        ]
        return f'<ul>{"".join(ingredients_list)}</ul>'
    return 'Нет ингредиентов'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_recipes_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'))

    @admin.display(description='Рецептов тэгом', ordering='recipes_total')
    def get_recipes_count(self, obj):
        return obj.recipes_total


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'get_recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'))

    @admin.display(description='Использований в рецептах',
                   ordering='recipes_total')
    def get_recipes_count(self, obj):
        return obj.recipes_total


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 2
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    autocomplete_fields = ('ingredient',)
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'cooking_time',
                    'author',
                    'get_tags_list',
                    'get_ingredients_list',
                    'get_favorite_count',
                    'get_image')
    search_fields = ('name', 'tags__name')
    list_filter = ('author__username', 'tags__name')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request)
            .prefetch_related('tags', 'recipe_ingredients__ingredient')
            .annotate(favorite_total=Count('favorite')))
        return queryset

    @admin.display(description='Тэги')
    @mark_safe
    def get_tags_list(self, obj):
        if obj.tags.exists():
            tags = obj.tags.values_list('name', flat=True)
            tags_list = [f'<li>{tag}</li>' for tag in tags]
            return f'<ul>{"".join(tags_list)}</ul>'
        return 'Нет тэгов'

    @admin.display(description='Ингредиенты')
    @mark_safe
    def get_ingredients_list(self, obj):
        ingredients = (obj.recipe_ingredients
                       .select_related('ingredient').all())
        return get_ingredients_list(ingredients)

    @admin.display(description='Добавлений в избранное',
                   ordering='favorite_total')
    def get_favorite_count(self, obj):
        return obj.favorite_total

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="75" height="75" />'
        return 'Нет изображения'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'measurement_unit', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ('recipe', 'ingredient')

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('ingredient')
        return queryset

    @admin.display(description='Ед. изм')
    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class UserRecipeBase(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'get_ingredients')
    search_fields = ('user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')

    class Meta:
        abstract = True

    @admin.display(description='Ингредиенты')
    @mark_safe
    def get_ingredients(self, obj):
        ingredients = (obj.recipe.recipe_ingredients
                       .select_related('ingredient').all())
        return get_ingredients_list(ingredients)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeBase):
    pass


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeBase):
    pass
