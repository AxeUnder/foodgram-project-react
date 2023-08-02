from rest_framework import routers
from django.urls import path, include

from .views import index, CustomUserViewSet, TagViewSet, RecipeViewwSet


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewwSet)

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
