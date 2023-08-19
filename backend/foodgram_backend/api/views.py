# api/view.py
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag, Recipe
from users.models import CustomUser, Subscription
from .serializers import (
    CustomUserSerializer,
    CustomUserSignUpSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer, RecipeMinifiedSerializer, SubscriptionSerializer
)


class CustomUserViewSet(UserViewSet):
    """ViewSet модели пользователей"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserSignUpSerializer
        return CustomUserSerializer

    def get_subscribed_recipes(self, user):
        subscribed_users = user.following.all()
        subscribed_recipes = Recipe.objects.filter(author__in=subscribed_users, pub_date__lte=date.today())
        return subscribed_recipes

    def paginate_and_serialize(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": self.request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={"request": self.request})
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        is_subscribed = request.query_params.get('is_subscribed', False)

        if is_subscribed:
            user = request.user
            queryset = CustomUser.objects.prefetch_related('recipes').filter(subscriptions__user=user)
        else:
            queryset = CustomUser.objects.prefetch_related('recipes').all()

        return self.paginate_and_serialize(queryset)

    @action(detail=False, methods=['get'], url_path='subscriptions', url_name='list_subscriptions')
    def list_subscriptions(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)

        response_serializer = SubscriptionSerializer(page, many=True, context={'request': request})

        paginated_response = self.get_paginated_response(response_serializer.data)

        return paginated_response

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe', url_name='subscribe')
    def subscribe(self, request, pk=None, **kwargs):
        target_user = get_object_or_404(get_user_model(), id=pk)

        if request.user.pk == target_user.pk:
            return Response({"detail": "Невозможно подписаться на самого себя."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(user=request.user, author=target_user)
            if created:
                return Response({"detail": "Подписка успешно добавлена"},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Вы уже подписаны на этого пользователя"},
                                status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(user=request.user, author=target_user)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response({"detail": "Подписка не найдена"},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']

            if self.request.user.check_password(current_password):
                self.request.user.set_password(new_password)
                self.request.user.save()
                return Response(status=204)
            else:
                return Response({'detail': 'Пароли не совпадают.'}, status=400)
        else:
            return Response(serializer.errors, status=400)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.request.query_params.get('recipes_limit', None)

        if recipes_limit is not None:
            recipes_queryset = instance.recipes.all()[:recipes_limit]
        else:
            recipes_queryset = instance.recipes.all()

        representation['recipes'] = RecipeMinifiedSerializer(recipes_queryset, many=True).data
        return representation

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TagViewSet(ModelViewSet):
    """ViewSet модели тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TagListView(APIView):
    """Представление для получения списка тегов"""
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


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
        recipes = Recipe.objects.select_related('author').prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()
