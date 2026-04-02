from django.contrib import admin

from api.models.favorite import Favorite
from api.models.shopping_cart import ShoppingCart


class UserRecipeBase(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')

    class Meta:
        abstract = True


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeBase):
    pass


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeBase):
    pass
