from django.contrib import admin
from .models import User


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


admin.site.register(User, UserAdmin)