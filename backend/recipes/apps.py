from django.apps import AppConfig


class RecipesConfig(AppConfig):
    name = 'recipes'
    verbose_name = 'Рецепты'

    def ready(self):
        import recipes.signals  # noqa