from rest_framework import routers
from django.urls import path, include

from .views import index


router = routers.DefaultRouter()

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
]
