from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'pk',
        'name',
        'tags',
        'author',
        'text',
        'ingredients',
        'image'
    )
    list_display_links = ('name',)
    search_fields = (
        'name',
        'author',
        'text',
        'ingredients'
    )
    list_editable = (
        'name',
        'author',
    )
    list_filter = ('tags',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_display_links = ('name',)
    list_filter = ('measurement_unit',)
    list_editable = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'
