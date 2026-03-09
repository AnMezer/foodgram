from django.contrib import admin

from api.models.models import Subscribe, ShoppingCart, Favorite


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'user')
    search_fields = ('subscriber', 'user')
    autocomplete_fields = ('subscriber', 'user')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')

