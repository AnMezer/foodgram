from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.models import Recipe

User = get_user_model()

class UserBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        abstract = True

class UserRecipeBase(UserBase):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')