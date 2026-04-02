from hashids import Hashids

from project_settings import config

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
