# api/view.py
from datetime import date

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from django.utils.translation import gettext_lazy as _

from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag, Recipe, Ingredient, ShoppingCart
from users.models import CustomUser, Subscription
from .serializers import (
    CustomUserSerializer,
    CustomUserSignUpSerializer,
    TagSerializer,
    RecipeSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeMinifiedSerializer, SubscriptionSerializer
)
from .utils import process_shopping_list, generate_shopping_list_pdf, IsAuthenticatedOrReadOnly


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


class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    pagination_class = LimitOffsetPagination

    def get_user(self, id):
        return get_object_or_404(CustomUser, id=id)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'], url_path='subscriptions', url_name='list_subscriptions')
    def list_subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user).order_by('-id')
        paginator = LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset, context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe', url_name='subscribe')
    def subscribe(self, request, id=None):
        target_user = self.get_user(id)

        if request.user.pk == target_user.pk:
            return Response({"errors": "Невозможно подписаться на самого себя."},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscription.objects.get_or_create(user=request.user, author=target_user)
        if created:
            serializer = self.serializer_class(subscription, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Вы уже подписаны на этого пользователя"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='subscribe', url_name='unsubscribe')
    def unsubscribe(self, request, id=None):
        target_user = self.get_user(id)

        try:
            subscription = Subscription.objects.get(user=request.user, author=target_user)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response({"detail": "Подписка не найдена"},
                            status=status.HTTP_404_NOT_FOUND)


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


class IngredientViewSet(ModelViewSet):
    """ViewSet для получения ингредиентов"""
    serializer_class = IngredientSerializer
    lookup_field = 'id'
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__icontains=query)
        return queryset


class RecipeViewSet(ModelViewSet):
    """ViewSet модели рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

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
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()

        # Фильтрация по тегам
        tags = self.request.query_params.getlist('tags', [])
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        # Фильтрация по избранным
        is_favorited = self.request.query_params.get('is_favorited', None)
        if is_favorited is not None:
            favorited_recipes_ids = self.request.user.favorites_user.all().values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=favorited_recipes_ids) if int(is_favorited) else queryset.exclude(
                id__in=favorited_recipes_ids)

        # Фильтрация по корзине покупок
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart', None)
        if is_in_shopping_cart is not None:
            shopping_cart_recipe_ids = self.request.user.shopping_cart.all().values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=shopping_cart_recipe_ids) if int(is_in_shopping_cart) else queryset.exclude(
                id__in=shopping_cart_recipe_ids)

        return queryset

    @action(detail=True, methods=["post"], url_path='favorite', url_name='add_favorite', permission_classes=[IsAuthenticated])
    def add_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if not recipe.favorites_recipe.filter(user=user).exists():
            recipe.favorites_recipe.create(user=user)
            serializer = RecipeMinifiedSerializer(recipe, context={"request": request})
            response_data = {"id": serializer.data["id"], "name": serializer.data["name"],
                             "image": serializer.data["image"], "cooking_time": serializer.data["cooking_time"]}
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path='favorite', url_name='remove_favorite', permission_classes=[IsAuthenticated])
    def remove_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        fav_instance = recipe.favorites_recipe.filter(user=user).first()
        if fav_instance:
            fav_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"errors": "Рецепт не найден в избранных"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path='shopping_cart', url_name='add_to_shopping_cart',
            permission_classes=[IsAuthenticated])
    def add_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            ShoppingCart.objects.create(user=user, recipe_id=pk)
            serializer = RecipeMinifiedSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": "Рецепт уже в списке покупок"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path='shopping_cart', url_name='remove_from_shopping_cart',
            permission_classes=[IsAuthenticated])
    def remove_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        shopping_cart_instance = recipe.shopping_cart.filter(user=user).first()
        if shopping_cart_instance:
            shopping_cart_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"errors": "Рецепт не найден в списке покупок"}, status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.request.user.save()


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeMinifiedSerializer

    @action(detail=True, methods=["delete"], url_path='shopping_cart', url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        current_user_shopping_list = Recipe.objects.filter(shopping_cart__user=user)
        shopping_list_items = process_shopping_list(current_user_shopping_list)
        pdf = generate_shopping_list_pdf(shopping_list_items, user)

        response = FileResponse(pdf, content_type='application/pdf')
        filename = f'{user.username}_shopping_cart.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
