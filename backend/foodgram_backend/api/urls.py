# api/urls.py
from django.urls import path, include
from rest_framework import routers

from .views import CustomUserViewSet, TagViewSet, TagListView, RecipeViewSet


router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'users', CustomUserViewSet, basename='users-list')
router.register(r'users/set_password', CustomUserViewSet, basename='set_password')
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagViewSet.as_view({'get': 'retrieve'}), name='tag-detail')
]
