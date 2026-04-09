from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import TokenProxy

from users.models import Subscribe

admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_banned',
        'get_recipes_count',
        'get_subscribers_count',
        'get_followings_count',
        'get_avatar'
    )
    readonly_fields = ('get_avatar',)
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('is_banned', 'avatar', 'get_avatar')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'classes': ('wide',),
                'fields': ('first_name', 'last_name', 'email', 'avatar')}),
    )

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

    @admin.display(description='Текущий аватар')
    @mark_safe
    def get_avatar(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="75" height="75" />'
        return 'Нет аватара'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'user')
    search_fields = ('subscriber__username', 'user__username')
    autocomplete_fields = ('subscriber', 'user')
