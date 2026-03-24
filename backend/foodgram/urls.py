from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from api.views import UsersViewSet, TagsViewSet, IngredientsViewSet

router_v1 = routers.DefaultRouter()

router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('api/', include(router_v1.urls)),
    path('admin/', admin.site.urls),
    path('api/auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('api/auth/token/logout/', TokenDestroyView.as_view(), name='logout'),


]

if settings.DEBUG:
    DOCS_ROOT = settings.BASE_DIR.parent / 'docs'
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/api/docs/', document_root=DOCS_ROOT)