from pathlib import Path
from typing import Any, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HOSTS = ['localhost', '127.0.0.1']


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    DJANGO_SECRET_KEY: str = '111'
    DEBUG_MODE: bool = True
    ALLOWED_HOSTS: Union[list[str], str] = DEFAULT_HOSTS

    TAG_NAME_LENGTH: int = 32
    TAG_SLUG_LENGTH: int = 32

    INGREDIENT_NAME_LENGTH: int = 128
    MEAS_UNIT_LENGTH: int = 64

    RECIPE_NAME_LENGTH: int = 256
    MIN_COOKING_TIME: int = 1

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




