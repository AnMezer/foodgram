from api.v1.serializers.serializers import TagSerializer
from api.v1.views.viewsets import ListRetrieveBaseModel
from recipes.models import Tag


class TagsViewSet(ListRetrieveBaseModel):
    """Вьюсет для тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
