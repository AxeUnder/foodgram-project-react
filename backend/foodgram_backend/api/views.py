from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag, Recipe
from users.models import CustomUser
from .serializers import TagSerializer, RecipeSerializer, UserSerializer, RecipeCreateSerializer


def index(request):
    return HttpResponse('index')


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def dispatch(self, request, *args, **kwargs):
        """Логи запросов к db"""
        res = super().dispatch(request, *args, **kwargs)

        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            print('>>>>', q['sql'])

        return res

    def get_queryset(self):
        """Оптимизация запросов"""
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
