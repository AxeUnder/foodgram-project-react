from rest_framework import routers
from django.urls import path, include

from .views import CustomUserViewSet, TagViewSet, RecipeViewSet


router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
