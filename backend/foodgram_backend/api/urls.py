from rest_framework import routers
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import CustomUserViewSet, TagViewSet, RecipeViewSet


router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
# router.register(r'users/set_password', CustomUserViewSet, basename='set_password')
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/set_password/', CustomUserViewSet.as_view({'post': 'set_password'}), name='set_password'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
