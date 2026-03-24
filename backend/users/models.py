from django.db import models
from django.contrib.auth.models import AbstractUser

from project_settings import config


class CustomUser(AbstractUser):
    avatar = models.ImageField('Аватар', upload_to='avatars', blank=True)
    email = models.EmailField(unique=True, max_length=config.EMAIL_LENGTH)
    first_name = models.CharField('Имя', max_length=config.FIRST_NAME_LENGTH)
    last_name = models.CharField('Имя', max_length=config.LAST_NAME_LENGTH)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username