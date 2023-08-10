from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import render, HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import Tag, Recipe
from users.models import CustomUser
from .serializers import (
    CustomUserSerializer,
    CustomUserSignUpSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet модели пользователей"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'POST':
            return CustomUserSignUpSerializer
        return CustomUserSerializer


class TagViewSet(ModelViewSet):
    """ViewSet модели тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """ViewSet модели рецептов"""
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination

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

