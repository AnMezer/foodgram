from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.recipe import Recipe

User = get_user_model()


class UserBase(models.Model):
    """Абстрактная модель для поля user ForeignKey"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        abstract = True


class UserRecipeBase(UserBase):
    """Абстрактная модель для поля recipe ForeignKey"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        abstract = True
