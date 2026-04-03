from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count

from users.models import Subscribe

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_banned',
        'get_recipes_count',
        'get_subscribers_count',
        'get_followings_count'
    )
    search_fields = ('username', 'email')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'),
                                 subscribers_total=Count('subscribers'),
                                 followings_total=Count('subscribe'))

    @admin.display(description='Рецептов', ordering='recipes_total')
    def get_recipes_count(self, obj):
        return obj.recipes_total

    @admin.display(description='Подписчиков', ordering='subscribes_total')
    def get_subscribers_count(self, obj):
        return obj.subscribers_total

    @admin.display(description='Подписок', ordering='followings_total')
    def get_followings_count(self, obj):
        return obj.followings_total


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'user')
    search_fields = ('subscriber', 'user')
    autocomplete_fields = ('subscriber', 'user')
