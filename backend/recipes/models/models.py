from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from project_settings import config

User = get_user_model()

class Tag(models.Model):
    name = models.CharField('Тэг',
                            max_length=config.TAG_NAME_LENGTH,
                            unique=True,
                            help_text=f'Макс. {config.TAG_NAME_LENGTH} символа')
    slug = models.SlugField('Слаг',
                            max_length=config.TAG_SLUG_LENGTH,
                            unique=True,
                            help_text='Поле заполнится автоматически')


    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Ингредиент',
                            max_length=config.INGREDIENT_NAME_LENGTH,
                            unique=True,
                            help_text=f'Макс. {config.INGREDIENT_NAME_LENGTH} '
                                      f'символа')
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=config.MEAS_UNIT_LENGTH,
        help_text=f'Макс. {config.MEAS_UNIT_LENGTH} символов')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Рецепт',
        max_length=config.RECIPE_NAME_LENGTH,
        unique=True,
        help_text=f'Макс. {config.RECIPE_NAME_LENGTH} символов')
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (минут)',
        validators=[MinValueValidator(1)])
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    image = models.ImageField('Изображение рецепта',
                              upload_to='recipes.images',
                              blank=True)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField('Кол-во',
                                              validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return (f'{self.ingredient.name}[{self.ingredient.measurement_unit}] в рецепте'
                f' {self.recipe.name}')
