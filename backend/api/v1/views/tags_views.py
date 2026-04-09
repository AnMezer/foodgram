from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.v1.serializers.serializers import TagSerializer
from recipes.models import Tag


class TagsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    authentication_classes = ()
