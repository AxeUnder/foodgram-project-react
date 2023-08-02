from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
