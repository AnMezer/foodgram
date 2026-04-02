from django.core.validators import MinValueValidator
from django.db import models

from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Кол-во',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return (f'{self.ingredient.name}'
                f'[{self.ingredient.measurement_unit}] в рецепте'
                f' {self.recipe.name}')
