from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.v1.views.recipes_views import redirect_to_recipe

admin.site.site_header = 'Панель администратора Foodgram'

urlpatterns = [
    path('s/<str:hashed_id>/', redirect_to_recipe),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),

]

if settings.DEBUG:
    DOCS_ROOT = settings.BASE_DIR.parent / 'docs'
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/api/docs/', document_root=DOCS_ROOT)
