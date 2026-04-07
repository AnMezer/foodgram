from django.contrib.auth import get_user_model
from django.db import models
from pydantic import ValidationError

from recipes.models.base_models import UserBase

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
        return f'Подписка {self.subscriber.username} на {self.user.username}'
