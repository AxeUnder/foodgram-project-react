# api/mixins.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from users.models import Subscription
from recipes.models import Favorite


class CreateListViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = LimitOffsetPagination


class AddMixin:
    model = None

    def add_item(self, request, id=None):
        user = request.user
        content_object = self.get_object(id)

        if self.model.objects.filter(user=user, content_object=content_object).exists():
            return Response(
                {"detail": f"{content_object} уже добавлен"},
                status=status.HTTP_400_BAD_REQUEST)

        self.model.objects.create(user=user, content_object=content_object)
        return Response(status=status.HTTP_201_CREATED)


class RemoveMixin:
    model = None

    def remove_item(self, request, id=None):
        user = request.user
        content_object = self.get_object(id)

        item_instance = self.model.objects.filter(user=user, content_object=content_object).first()

        if not item_instance:
            return Response(
                {"detail": f"{content_object} не найден"},
                status=status.HTTP_404_NOT_FOUND)

        item_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
