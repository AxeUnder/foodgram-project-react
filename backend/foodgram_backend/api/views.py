from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag, Recipe
from .serializers import TagSerializer, RecipeSerializer


def index(request):
    return HttpResponse('index')


class CustomUserViewSet(UserViewSet):
    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewwSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
