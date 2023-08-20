# api/urls.py
from django.urls import path, include, re_path
from rest_framework import routers

from .views import CustomUserViewSet, TagViewSet, TagListView, RecipeViewSet, SubscriptionViewSet, IngredientViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagViewSet.as_view({'get': 'retrieve'}), name='tag-detail'),
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list_subscriptions'}), name='subscriptions-list'),
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view({'post': 'subscribe', 'delete': 'unsubscribe'}), name='subscribe-unsubscribe'),
    path('', include(router.urls)),
]
