from django.contrib.auth import get_user_model
from djoser.serializers import (SetPasswordSerializer as
                                DjoserSetPasswordSerializer)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api.fields import Base64ImageField
from project_settings import config
from recipes.models.favorite import Favorite
from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe
from recipes.models.recipe_ingredient import RecipeIngredient
from recipes.models.shopping_cart import ShoppingCart
from recipes.models.tag import Tag
from users.models.subscribe import Subscribe

User = get_user_model()


class SetPasswordSerializer(DjoserSetPasswordSerializer):
    """Сериализатор для смены пароля"""
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class AvatarEditSerializer(serializers.ModelSerializer):
    """Сериализатор аватара"""
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


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
    first_name, last_name, email, id
    """

    class Meta(UsernameSerializer.Meta):
        fields = UsernameSerializer.Meta.fields + ('first_name', 'last_name',
                                                   'email', 'id')


class UserCreateSerializer(UserPrimaryFieldsSerializer):
    """Сериализатор для создания пользователя"""

    class Meta(UserPrimaryFieldsSerializer.Meta):
        fields = UserPrimaryFieldsSerializer.Meta.fields + ('password',)
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

        if not request or not request.user.is_authenticated:
            return False
        subscriber = request.user

        return Subscribe.objects.filter(user=obj,
                                        subscriber=subscriber).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.Serializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=True)
    amount = serializers.IntegerField(min_value=config.INGREDIENT_AMOUNT_MIN,
                                      max_value=config.INGREDIENT_AMOUNT_MAX,
                                      required=True)


class IngredientRecipeSerializer(IngredientAmountSerializer):
    """Сериализатор для ингредиентов в рецептах"""
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенной информации о рецепте"""
    name = serializers.CharField(max_length=config.RECIPE_NAME_LENGTH,
                                 required=True,
                                 allow_blank=False)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=config.COOKING_TIME_MIN,
                                            max_value=config.COOKING_TIME_MAX,
                                            required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(RecipeShortSerializer):
    """Сериализатор для чтения полной информации о рецепте"""
    author = UsersListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(source='recipe_ingredients',
                                             many=True,
                                             read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.CharField(read_only=True)

    class Meta(RecipeShortSerializer.Meta):
        fields = RecipeShortSerializer.Meta.fields + ('tags',
                                                      'author',
                                                      'ingredients',
                                                      'text',
                                                      'is_favorited',
                                                      'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        if not Favorite.objects.filter(user_id=request.user.pk,
                                       recipe_id=obj.pk).exists():
            return False
        return True

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        if not ShoppingCart.objects.filter(user_id=request.user.pk,
                                           recipe_id=obj.pk).exists():
            return False
        return True


class RecipeSerializer(RecipeShortSerializer):
    """Сериализатор для сохранения рецепта"""
    author = UsersListSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True,
                                             required=True,
                                             write_only=True,
                                             allow_empty=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True,
                                              allow_empty=False,
                                              write_only=True)
    text = serializers.CharField(required=True, allow_blank=False)

    class Meta(RecipeShortSerializer.Meta):
        model = Recipe
        fields = RecipeShortSerializer.Meta.fields + (
            'tags', 'author', 'ingredients', 'text')

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Нельзя дублировать тэги')
        return value

    def validate_ingredients(self, value):
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Нельзя дублировать ингредиенты')
        return value

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH':
            required_fields = ('ingredients', 'tags',
                               'name', 'text', 'cooking_time')
            missing_fields = []
            for field in required_fields:
                if field not in self.initial_data:
                    missing_fields.append(field)
            if missing_fields:
                raise serializers.ValidationError(
                    f'Поля {", ".join(missing_fields)} '
                    f'обязательны для заполнения')
        return attrs

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        validated_data['author'] = self.context['request'].user

        instance = Recipe.objects.create(**validated_data)
        instance.tags.set(tags)
        self.save_ingredients(instance, ingredients)

        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)

        instance.tags.set(tags)

        RecipeIngredient.objects.all().delete()
        self.save_ingredients(instance, ingredients)

        return instance

    def save_ingredients(self, recipe, ingredients):
        """Сохраняет ингредиенты рецепта"""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']) for ingredient in ingredients)


class SubscribeSerializer(UsersListSerializer):
    """Сериализатор оформления подписки"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersListSerializer.Meta):
        fields = UsersListSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes_count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except Exception:
                raise serializers.ValidationError(
                    'recipes_limit должен быть целым числом')
            if int(recipes_limit) <= 0:
                raise serializers.ValidationError(
                    'recipes_limit должен быть положительным')
            recipes = recipes[:recipes_limit]
        return RecipeShortSerializer(recipes, many=True,
                                     context=self.context).data
