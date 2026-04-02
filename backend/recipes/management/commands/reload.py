import csv
import os

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.base import ModelBase

from .exceptions import ModelNotFoundError

User = get_user_model()
IMPORT_QUEUE = {
    'users': ['customuser'],
    'recipes': ['ingredient', 'recipe', 'tag']

}
M2M_TABLES = {
    'recipes': ['recipeingredient', 'recipe_tags'],
    'users': ['subscribe']
}
PATH = settings.BASE_DIR.parent / 'data'
SUPERUSER = {
    'username': 'admin',
    'first_name': 'admin_first',
    'last_name': 'admin_last',
    'email': 'admin@admin.ru',
    'password': 'admin',
    'is_superuser': True
}


class Command(BaseCommand):
    help = 'Очищает БД, заполняет тестовыми данными, создает учетку суперюзера'

    def check_files(self, path: str) -> None:
        """Проверяет наличие файлов в папке

        Args:
            path: Путь к папке с файлами
        Raises:
            FileNotFoundError: Если файл отсутствует
        """
        not_exist_files = []
        tables_list = {**IMPORT_QUEUE, **M2M_TABLES}.values()
        for tables in tables_list:
            for table in tables:

                file_path = os.path.join(path, f'{table}.csv')
                if not os.path.exists(f'{file_path}'):
                    not_exist_files.append(f'{table}.csv')
        if not_exist_files:
            error_message = (f'Файл(ы) не найден(ы): '
                             f'{", ".join(not_exist_files)}. Path:{PATH}')
            raise FileNotFoundError(error_message)

    def get_model(self, app: str, table: str) -> ModelBase:
        """Возвращает модель приложения по названию таблицы

        Args:
            app: Название приложения
            table: Название таблицы

        Raises:
            ModelNotFound: Если модель не найдена
        """
        try:
            model = apps.get_model(app, table)
            return model
        except (LookupError, ValueError) as e:
            error_message = (
                f'Ошибка при поиске модели {table} в приложении {app}. {e}')
            raise ModelNotFoundError(error_message)

    def clean_row(self, row: dict) -> dict[str, str | int | None] | None:
        """Проверяет на корректность значения полей

        Args:
            row: Словарь с исходными полями

        Returns:
            cleaned_row - если значения пригодны для записи в БД
            None - если значения использовать нельзя.
        """
        cleaned_row: dict[str, str | int | None] = {}
        for field, value in row.items():

            # Проверяем, что значения полей ForeignKey можно привести к int
            if field.endswith('_id'):
                try:
                    cleaned_row[field] = int(value)
                except Exception:
                    return None

            # Если данные изначально корректны, сохраняем, как есть
            else:
                cleaned_row[field] = value

        return cleaned_row

    def create_superuser(self) -> None:
        """Добавляет учетку суперпользователя"""
        User.objects.create_superuser(**SUPERUSER)
        self.stdout.write(self.style.SUCCESS('superuser создан'))

    def fill_table(self, app, table):
        """Заполняет таблицу"""
        self.stdout.write(self.style.NOTICE(
            f'Обрабатываю приложение {app}, таблицу {table}'))

        file_path = os.path.join(PATH, f'{table}.csv')
        model = self.get_model(app, table)

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            rows = list(reader)
            with transaction.atomic():
                for row in rows:
                    cleaned_row = self.clean_row(row)
                    if cleaned_row:
                        model.objects.create(**cleaned_row)
                    else:
                        self.stdout.write(self.style.ERROR(
                            f'Строка:{row} -- Не загружена'))
                self.stdout.write(self.style.SUCCESS(
                    f'Таблица {table} загружена'))

    def handle(self, *args, **options):
        self.check_files(PATH)
        call_command('flush', '--noinput')

        self.stdout.write(self.style.SUCCESS('База данных очищена'))

        try:
            for app, tables in IMPORT_QUEUE.items():
                for table in tables:
                    self.fill_table(app, table)

            for app, tables in M2M_TABLES.items():
                for table in tables:
                    self.fill_table(app, table)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'{e}'))

        self.create_superuser()
