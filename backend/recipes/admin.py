from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count

from .models.ingredient import Ingredient
from .models.recipe import Recipe
from .models.recipe_ingredient import RecipeIngredient
from .models.tag import Tag

User = get_user_model()
admin.site.unregister(Group)


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
    search_fields = ('name',)

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
    list_display = ('name', 'cooking_time',
                    'get_tags_list',
                    'get_ingredients_list',
                    'get_favorite_count')
    search_fields = ('name',)
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(
            'tags', 'recipe_ingredients__ingredient').annotate(
            favorite_total=Count('favorite')
        )
        return queryset

    @admin.display(description='Тэги')
    def get_tags_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def get_ingredients_list(self, obj):
        return ', '.join(
            ingredient.name for ingredient in obj.ingredients.all())

    @admin.display(description='Добавлений в избранное',
                   ordering='favorite_total')
    def get_favorite_count(self, obj):
        return obj.favorite_total


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'measurement_unit', 'amount')
    search_fields = ('recipe', 'ingredient')
    autocomplete_fields = ('recipe', 'ingredient')

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('ingredient')
        return queryset

    @admin.display(description='Ед. изм')
    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
