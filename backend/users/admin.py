from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Админ-модель пользователей"""
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role'
    )
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('role',)
    list_editable = (
        'email',
        'role',
        'first_name',
        'last_name'
    )
    list_fields = ('first_name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-модель подписок"""
    list_display = (
        'pk',
        'user',
        'author'
    )
    search_fields = (
        'user',
        'author'
    )
    list_editable = (
        'user',
        'author'
    )
    empty_value_display = '-пусто-'
