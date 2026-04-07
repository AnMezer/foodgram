from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet


class ListRetrieveBaseModel(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    authentication_classes = ()
