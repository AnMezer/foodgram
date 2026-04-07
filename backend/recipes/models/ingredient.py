from django.db import models

from project_settings import config


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
        constraints = [
            models.UniqueConstraint(fields=('name', 'measurement_unit'),
                                    name='unique_ingredient_measurement_unit')
        ]

    def __str__(self):
        return f'{self.name}_{self.measurement_unit}'
