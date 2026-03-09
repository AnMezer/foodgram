from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count
from django.template.backends.django import reraise

from .models.models import Tag, Recipe, Ingredient, RecipeIngredient

User = get_user_model()
admin.site.unregister(Group)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'recipes_count'
    )
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


    @admin.display(description='Рецептов с этим тэгом',
                   ordering='recipes_count')
    def recipes_count(self, obj):
        return obj.recipes_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_count=Count('recipes'))


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    autocomplete_fields = ('ingredient',)
    fields = ('ingredient','amount')



@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooking_time', 'tags_list', 'ingredients_list')
    search_fields = ('name',)
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(
            'tags', 'recipe_ingredients__ingredient')
        return queryset

    @admin.display(description='Тэги')
    def tags_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        return ', '.join(ingredient.name for ingredient in obj.ingredients.all())


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
