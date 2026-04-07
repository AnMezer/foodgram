# flake8: noqa
from importlib import import_module
from pathlib import Path
from typing import Any, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HOSTS = ['localhost', '127.0.0.1', 'host.docker.internal']
DEFAULT_CSRF_TRUSTED_ORIGINS = ['http://localhost:8000',
                                'http://127.0.0.1:8000']

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    POSTGRES_DB: str = 'django'
    POSTGRES_USER: str = 'django'
    POSTGRES_PASSWORD: str = ''
    DB_HOST: str = ''
    DB_PORT: int = 5431

    DJANGO_SECRET_KEY: str = '111'
    DEBUG_MODE: bool = True
    ALLOWED_HOSTS: Union[list[str], str] = DEFAULT_HOSTS
    CSRF_TRUSTED_ORIGINS: Union[list[str], str] = DEFAULT_CSRF_TRUSTED_ORIGINS

    # --- Переменные ----
    FIRST_NAME_LENGTH: int = 150
    LAST_NAME_LENGTH: int = 150
    USERNAME_LENGTH: int = 150

    TAG_NAME_LENGTH: int = 32
    TAG_SLUG_LENGTH: int = 32

    INGREDIENT_NAME_LENGTH: int = 128
    MEAS_UNIT_LENGTH: int = 64
    INGREDIENT_AMOUNT_MIN: int = 1
    INGREDIENT_AMOUNT_MAX: int = 999


    RECIPE_NAME_LENGTH: int = 256
    COOKING_TIME_MIN: int = 1
    COOKING_TIME_MAX: int = 480

    EMAIL_LENGTH: int = 254

    FORBIDDEN_USERNAMES: set = ('me',)
    REGEX_STAMP: str = r'^[\w.@+-]+\Z'

    HASHIDS_SALT: str = 'foodgram'
    HASH_ID_MIN_LENGTH: int = 6

    PAGESIZE: int = 6

    FIELDS_FOR_ANOTHER_SAVE_RECIPE: set = ('tags', 'ingredients', 'image')
    DEFAULT_RECIPE_IMAGE_PATH: str = '/media/recipes/images/default.png'
    # ---------------------

    ENDPOINT_VERSIONS: dict[str, str] = {
        'users': 'v1',
        'tags': 'v1',
        'recipes': 'v1',
        'ingredients': 'v1',
        'favorite': 'v1'
    }

    DEFAULT_ENDPOINT_VERSION: str = 'v1'

    def get_viewset(self, endpoint_name, viewset_name):
        """Возвращает ViewSet для выбранной версии эндпоинта"""
        version = self.ENDPOINT_VERSIONS.get(endpoint_name,
                                             self.DEFAULT_ENDPOINT_VERSION)
        file_name = f'{endpoint_name}_views'
        app = 'api'
        module_path = f'{app}.{version}.views.{file_name}'
        module = import_module(module_path)
        viewset = getattr(module, viewset_name)
        return viewset
    # -------------------

    @field_validator('CSRF_TRUSTED_ORIGINS', mode='before')
    @classmethod
    def validate_csrf_rtusted_origins(cls, raw_csrf: Any) -> list[str]:
        global DEFAULT_CSRF_TRUSTED_ORIGINS
        if not raw_csrf:
            return DEFAULT_CSRF_TRUSTED_ORIGINS
        if isinstance(raw_csrf, list):
            return raw_csrf
        if isinstance(raw_csrf, str):
            try:
                hosts = [host.strip() for host in raw_csrf.split(',')
                         if host.strip()]
                return hosts
            except Exception:
                return DEFAULT_CSRF_TRUSTED_ORIGINS
        return DEFAULT_CSRF_TRUSTED_ORIGINS

    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def validate_hosts(cls, raw_hosts: Any) -> list[str]:
        global DEFAULT_HOSTS
        if not raw_hosts:
            return DEFAULT_HOSTS
        if isinstance(raw_hosts, list):
            return raw_hosts
        if isinstance(raw_hosts, str):
            try:
                hosts = [host.strip() for host in raw_hosts.split(',')
                         if host.strip()]
                return hosts
            except Exception:
                return DEFAULT_HOSTS
        return DEFAULT_HOSTS


config = Config()





