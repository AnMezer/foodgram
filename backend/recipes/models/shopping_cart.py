from recipes.models.base_models import UserRecipeBase


class ShoppingCart(UserRecipeBase):
    """Модель корзины покупок"""
    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return f'Список покупок для {self.user} - {self.recipe.name}'
