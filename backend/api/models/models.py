from django.db import models
from django.contrib.auth import get_user_model
from pydantic import ValidationError

from recipes.models.models import Recipe
from .base_models import UserBase, UserRecipeBase

User = get_user_model()


class Subscribe(UserBase):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE,
                                   verbose_name='Подписчик',
                                   related_name='subscribers',)

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=('user', 'subscriber'), name='unique_subscribe')
        ]

    def clean(self):
        super().clean()
        if self.user and self.subscriber:
            if self.subscriber == self.user:
                raise ValidationError('Нельзя подписаться на самого себя')

    def __str__(self):
        return f'Подписка {self.subscriber.name} на {self.user.name}'

class ShoppingCart(UserRecipeBase):

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return f'Список покупок для {self.user} - {self.recipe.name}'

class Favorite(UserRecipeBase):

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Избранное пользователя {self.user}'