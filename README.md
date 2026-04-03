**Foodgram** — это веб-приложение, где пользователи могут публиковать кулинарные рецепты, подписываться на любимых авторов, добавлять блюда в избранное и формировать список покупок.

## Возможности

- Регистрация и авторизация пользователей
- Создание, редактирование и удаление рецептов
- Фильтрация рецептов по тегам и ингредиентам
- Добавление рецептов в «Избранное»
- Формирование списка покупок с возможностью скачивания
- Подписка на других пользователей

**Бэкенд**: Python 3.12, Django 6.0.3, Django REST Framework, PostgreSQL
**Фронтенд**: React, TypeScript
**Инфраструктура** Docker, Docker Compose, Nginx
**CI/CD**: GitHub Actions, Docker Hub

Для запуска локально:

1. Создайте .env файл по образцу (.env.example)
находясь в папке /foodgram/ выполните:
```
docker compose -f docker-compose.production.yml up
```

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

```
CONTAINER=$(docker compose -f docker-compose.production.yml ps -q backend)

docker cp ./data $CONTAINER:/app/data

docker compose -f docker-compose.production.yml exec backend python manage.py reload
```

После запуска проект станет доступным по адресу: http://127.0.0.1:8000

[Полная документация к эндпоинтам](https://anmezer.github.io/foodgram/)

### Тестовые данные
Для быстрого старта в проекте предусмотрены:   
- тестовые данные /foodgram/data/  
- команда reload - очищает БД, наполняет тестовыми данными, создает учетную запись суперпользователя

Для наполнения БД выполните в папке /foodgram/backend/  

```
python manage.py reload
```

#### Админ панель
Доступна по адресу http://127.0.0.1:8000/admin  
Данные супервользователя по умолчанию:  
admin@admin.ru  
admin
