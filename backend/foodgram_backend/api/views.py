# api/view.py
from datetime import date

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

    def list(self, request, *args, **kwargs):
        is_subscribed = request.query_params.get('is_subscribed', False)

        if is_subscribed:
            user = request.user
            subscribed = Exists(Subscription.objects.filter(user=user, author=OuterRef('pk')))
            queryset = CustomUser.objects.annotate(is_subscribed=subscribed,
                                                   recipes_count=Count('recipes'))
            queryset = queryset.filter(is_subscribed=True)
        else:
            queryset = CustomUser.objects.all().annotate(recipes_count=Count('recipes'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='subscriptions', url_name='list_subscriptions')
    def list_subscriptions(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        subscribed_authors = CustomUser.objects.filter(subscriptions__user=request.user)
        page = self.paginate_queryset(subscribed_authors)

        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        response_serializer = SubscriptionSerializer(page, many=True,
                                                     context={'request': request, 'recipes_limit': recipes_limit})

        # Used list comprehension to set all is_subscribed to True
        serialized_data = [{**item, "is_subscribed": True} for item in response_serializer.data]

        # Create paginated_response and set the results to the updated serialized_data
        paginated_response = self.get_paginated_response(response_serializer.data)
        paginated_response.data["results"] = serialized_data

        return paginated_response

    @action(detail=True, methods=['post'], url_path='subscribe', url_name='subscribe')
    def subscribe(self, request, id=None):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        author = self.get_object()

        if Subscription.objects.filter(user=request.user, author=author).exists():
            return Response({"Вы уже подписаны на этого пользователя"},
                            status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(user=request.user, author=author)

        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        response_serializer = SubscriptionSerializer(author, context={'request': request,
                                                                      'recipes_limit': recipes_limit})
        response_serializer.data["is_subscribed"] = True
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='unsubscribe', url_name='unsubscribe')
    def unsubscribe(self, request, id=None):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        author = self.get_object()

        subscription = Subscription.objects.filter(user=request.user, author=author).first()

        if not subscription:
            return Response({"Вы не подписаны на этого пользователя"},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        response_serializer = SubscriptionSerializer(author, context={'request': request,
                                                                      'recipes_limit': recipes_limit})
        response_serializer.data["is_subscribed"] = False
        return Response(response_serializer.data, status=status.HTTP_204_NO_CONTENT)

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
        recipes_limit = self.context.get('recipes_limit', None)

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
        self.request.user.save()
