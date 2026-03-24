import os.path

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
import base64
from django.core.files.base import ContentFile

from api.models.models import Subscribe
from project_settings import config
from recipes.models.models import Tag

User = get_user_model()

class Base64ImageField(serializers.ImageField):
    """Сериализатор для работы с изображениями"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if not value:
            return None
        return value.url

class AvatarEditSerializer(serializers.ModelSerializer):
    """Сериализатор аватара"""
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)

    def save(self, **kwargs):
        user = self.instance
        avatar_img = self.validated_data['avatar']

        if user.avatar:
            user.avatar.delete()

        _, ext = os.path.splitext(avatar_img.name)
        new_file_name = f'{user.id}_{user.username}{ext}'
        avatar_img.name = new_file_name

        return super().save()

class UsernameSerializer(serializers.ModelSerializer):
    """Сериализатор имени пользователя"""
    class Meta:
        model = User
        fields = ('username',)

    def validate_username(self, value):
        username = value

        if username.lower() in config.FORBIDDEN_USERNAMES:
            raise serializers.ValidationError(
                f'Имя пользователя {username} запрещено.')

        return value

class UserPrimaryFieldsSerializer(UsernameSerializer):
    """Сериализатор базовых полей пользователя:
    first_name', last_name, email, id
    """
    class Meta(UsernameSerializer.Meta):
        fields = UsernameSerializer.Meta.fields + ('first_name',
                                                   'last_name',
                                                   'email', 'id')

class UserCreateSerializer(UsernameSerializer):
    """Сериализатор для создания пользователя"""
    class Meta(UsernameSerializer.Meta):
        fields = UsernameSerializer.Meta.fields + ('password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UsersListSerializer(UserPrimaryFieldsSerializer):
    """Сериализатор списка пользователей"""
    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserPrimaryFieldsSerializer.Meta):
        fields = UserPrimaryFieldsSerializer.Meta.fields + ('avatar',
                                                            'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if not request.user.is_authenticated:
            return False
        subscriber = request.user
        return Subscribe.objects.filter(user=obj,
                                        subscriber=subscriber).exists()

class IdNameSlugSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')