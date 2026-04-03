import os

from django.contrib.auth.models import AbstractUser
from django.db import models

from project_settings import config


def get_user_avatar_path(instance, filename):
    """Возвращает путь/имя_файла для аватара пользователя"""
    _, ext = os.path.splitext(filename)
    new_file_name = f'{instance.username}{ext}'
    return f'users/{new_file_name}'


class CustomUser(AbstractUser):
    avatar = models.ImageField('Аватар',
                               upload_to=get_user_avatar_path,
                               blank=True)
    email = models.EmailField(unique=True, max_length=config.EMAIL_LENGTH)
    first_name = models.CharField('Имя', max_length=config.FIRST_NAME_LENGTH)
    last_name = models.CharField('Имя', max_length=config.LAST_NAME_LENGTH)
    is_banned = models.BooleanField('Заблокирован', default=False)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def recipes_count(self):
        """Возвращает кол-во рецептов созданных пользователем"""
        return self.recipes.count

    def __str__(self):
        return self.username
