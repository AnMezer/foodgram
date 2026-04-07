from django.db.models import Sum
from django.http import HttpResponse
from hashids import Hashids

from project_settings import config
from recipes.models import RecipeIngredient

hashids = Hashids(salt=config.HASHIDS_SALT,
                  min_length=config.HASH_ID_MIN_LENGTH)


def encode_id(recipe_id: int):
    """Возвращает закодированный id рецепта"""
    return hashids.encode(recipe_id)


def decode_id(encoded_id: str):
    """Возвращает id рецепта из кода"""
    decoded = hashids.decode(encoded_id)

    if decoded and isinstance(decoded[0], int):
        decoded_id = decoded[0]
    else:
        decoded_id = None

    return decoded_id


def get_bool(value: str):
    """Преобразует входящую строку в булево значение"""
    if value and value == '1':
        return True
    return False


def get_shopping_list(user):
    ingredients = (RecipeIngredient.objects
                   .filter(recipe__shoppingcart__user=user)
                   .values('ingredient__name',
                           'ingredient__measurement_unit')
                   .annotate(total_amount=Sum('amount')))

    shopping_list = ['СПИСОК ПОКУПОК:\n']
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        amount = ingredient['total_amount']
        meas_unit = ingredient['ingredient__measurement_unit']
        shopping_list.append(f'{" " * 4}-- {name}: {amount} {meas_unit}')
    result = '\n'.join(shopping_list)

    response = HttpResponse(result,
                            content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"')
    return response
