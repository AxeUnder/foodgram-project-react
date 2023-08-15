# api/urls.py
from django.urls import path, include
from rest_framework import routers

from .views import CustomUserViewSet, TagViewSet, TagListView, RecipeViewSet

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
# router.register(r'users', CustomUserViewSet, basename='users-list')
# router.register(r'users/set_password', CustomUserViewSet, basename='set_password')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes', RecipeViewSet, basename='recipes-list')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagViewSet.as_view({'get': 'retrieve'}), name='tag-detail'),
    path('', include(router.urls)),
]
