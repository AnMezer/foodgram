
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from project_settings import config

router = routers.DefaultRouter()

router.register('users',
                config.get_viewset('users', 'UsersViewSet'),
                basename='users')
router.register('tags',
                config.get_viewset('tags', 'TagsViewSet'),
                basename='tags')
router.register('ingredients',
                config.get_viewset('ingredients', 'IngredientsViewSet'),
                basename='ingredients')
router.register('recipes',
                config.get_viewset('recipes', 'RecipesViewSet'),
                basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
]
