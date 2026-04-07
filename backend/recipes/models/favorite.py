from recipes.models.base_models import UserRecipeBase


class Favorite(UserRecipeBase):
    """Модель избранных рецептов"""
    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Избранное пользователя {self.user}'
