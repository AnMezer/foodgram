import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import \
    SetPasswordSerializer as DjoserSetPasswordSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api.models.favorite import Favorite
from api.models.shopping_cart import ShoppingCart
from project_settings import config
from recipes.models.ingredient import Ingredient
from recipes.models.recipe import Recipe
from recipes.models.recipe_ingredient import RecipeIngredient
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
        request = self.context.get('request')
        if not request:
            return None
        return request.build_absolute_uri(value.url)


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

        if not request.user.is_authenticated:
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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенной информации о рецепте"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(RecipeShortSerializer):
    """Сериализатор для полной информации о рецепте"""
    author = UsersListSerializer(read_only=True)
    ingredients = serializers.ListField(child=serializers.DictField(),
                                        required=True,
                                        allow_empty=False,
                                        write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True,
                                              allow_empty=False,
                                              write_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeShortSerializer.Meta):
        model = Recipe
        fields = RecipeShortSerializer.Meta.fields + (
            'tags', 'author', 'ingredients',
            'text', 'is_favorited', 'is_in_shopping_cart')

    def validate_tags(self, value):
        tags_id = value
        if not tags_id:
            raise serializers.ValidationError('tags - обязательное поле')
        seen_tags = []
        for tag_id in tags_id:
            if tag_id in seen_tags:
                raise serializers.ValidationError('Нельзя дублировать тэги')
            seen_tags.append(tag_id)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError('ingredients обязательное поле')
        seen_ingredients = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_id = ingredient.get('id')
            if not amount or int(amount) < 1:
                raise serializers.ValidationError(
                    'amount - обязательное поле > 0 для ингредиента')
            if not ingredient_id:
                raise serializers.ValidationError(
                    'id - обязательное поле для ингредиента')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент id - {ingredient_id} отсутствует в базе')
            if ingredient_id in seen_ingredients:
                raise serializers.ValidationError(
                    'Нельзя дублировать ингредиенты')
            seen_ingredients.append(ingredient_id)
        return value

    def validate(self, attrs):
        required_fields = ('ingredients', 'tags', 'image',
                           'name', 'text', 'cooking_time')
        missing_fields = []
        for field in required_fields:
            if field not in self.initial_data:
                missing_fields.append(field)
        if missing_fields:
            raise serializers.ValidationError(
                f'Поля {", ".join(missing_fields)} обязательны для заполнения')
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tags'] = TagSerializer(instance.tags.all(),
                                    many=True,
                                    context=self.context).data
        ret['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(),
            many=True,
            context=self.context).data
        return ret

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not Favorite.objects.filter(user_id=request.user.pk,
                                       recipe_id=obj.pk).exists():
            return False
        return True

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not ShoppingCart.objects.filter(user_id=request.user.pk,
                                           recipe_id=obj.pk).exists():
            return False
        return True

    def create(self, validated_data):
        tags_id = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        validated_data['author'] = self.context['request'].user

        instance = Recipe.objects.create(**validated_data)

        if tags_id:
            instance.tags.set(tags_id)

        if ingredients:
            self.save_ingredients(instance, ingredients)

        return instance

    def update(self, instance, validated_data):
        tags_id = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if tags_id is not None:
            instance.tags.set(tags_id)
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.save_ingredients(instance, ingredients)

        return instance

    def save_ingredients(self, recipe, ingredients):
        """Сохраняет ингредиенты рецепта"""
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if not (ingredient_id and amount):
                continue

            ingredient_data = {
                'recipe_id': recipe.pk,
                'ingredient_id': ingredient_id,
                'amount': amount
            }
            RecipeIngredient.objects.create(**ingredient_data)


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
