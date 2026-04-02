from django.db import models
from slugify import slugify

from project_settings import config


class Tag(models.Model):
    name = models.CharField('Тэг',
                            max_length=config.TAG_NAME_LENGTH,
                            unique=True,
                            help_text=f'Макс. '
                                      f'{config.TAG_NAME_LENGTH} символа')
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
