from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import render, HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import Tag, Recipe
from users.models import CustomUser
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    UserSerializer,
    RecipeCreateSerializer,
    UserSignUpSerializer,
    UserEditSerializer
)


class CustomUserViewSet(UserViewSet):
    """ViewSet модели пользователей"""
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def dispatch(self, request, *args, **kwargs):
        """Логи запросов к db"""
        res = super().dispatch(request, *args, **kwargs)

        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            print('>>>>', q['sql'])

        return res

    @action(methods=['post'], detail=False, url_path='sign_up')
    def sign_up(request):
        serializer = UserSignUpSerializer(data=request.data)
        email = request.data.get('email')
        serializer.is_valid(raise_exception=True)
        try:
            user, created = CustomUser.objects.get_or_create(**serializer.validated_data)
        except IntegrityError:
            return Response(
                'Попробуй другой email или username',
                status=status.HTTP_400_BAD_REQUEST,
            )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Token Token Token',
            confirmation_code,
            'Foodgram',
            [email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,)
    def me(self, request):
        user = get_object_or_404(CustomUser, username=self.request.user)
        serializer = UserEditSerializer(user)
        if request.method == 'POST':
            serializer = UserEditSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            CustomUser.objects.get_or_create(**serializer.validated_data)
            return Response(
                serializer.validated_data, status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                'Попробуй другой email или username',
                status=status.HTTP_400_BAD_REQUEST,
            )


"""
def get_serializer_class(self):
if self.action == 'create':
return UserSingUpSerializer
return UserSerializer
"""


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

