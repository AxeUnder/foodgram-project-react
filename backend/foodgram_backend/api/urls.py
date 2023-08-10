from rest_framework import routers
from django.urls import path, include

from .views import CustomUserViewSet, TagViewSet, RecipeViewSet


router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'users/set_password', CustomUserViewSet, basename='set_password')
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
