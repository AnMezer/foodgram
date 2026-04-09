import os

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from slugify import slugify

from project_settings import config
from recipes.models.ingredient import Ingredient
from recipes.models.tag import Tag

User = get_user_model()


def get_recipe_image_path(instance, filename):
    """Возвращает путь/имя_файла для сохранения изображения рецепта """
    _, ext = os.path.splitext(filename)
    new_file_name = (f'{slugify(instance.name)}_'
                     f'{instance.author.username}{ext}')
    return f'recipes/images/{new_file_name}'


class Recipe(models.Model):
    name = models.CharField(
        'Рецепт',
        max_length=config.RECIPE_NAME_LENGTH,
        unique=True,
        help_text=f'Макс. {config.RECIPE_NAME_LENGTH} символов')
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'мин',
        validators=[
            MinValueValidator(config.COOKING_TIME_MIN),
            MaxValueValidator(config.COOKING_TIME_MAX)
        ])
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    image = models.ImageField('Изображение рецепта',
                              upload_to=get_recipe_image_path)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    created_at = models.DateTimeField('Дата создания', default=now)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
