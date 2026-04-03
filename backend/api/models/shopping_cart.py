from django.db import models

from api.models.base_models import UserRecipeBase


class ShoppingCart(UserRecipeBase):
    """Модель корзины покупок"""
    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [models.UniqueConstraint(
            fields=('user', 'recipe'), name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'Список покупок для {self.user} - {self.recipe.name}'
