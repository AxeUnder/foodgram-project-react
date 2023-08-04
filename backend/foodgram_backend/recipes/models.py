from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name=_('Имя тега'), max_length=200)
    color = models.CharField(verbose_name=_('HEX-цвет тега'), max_length=7)
    slug = models.SlugField(
        verbose_name=_('Слуг'),
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('id',)


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name=_('Тег'))
    name = models.CharField(
        verbose_name=_('Название рецепта'),
        max_length=200
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('Время готовки')
    )
    text = models.CharField(verbose_name=_('Текст'), max_length=250)
    image = models.ImageField(
        verbose_name=_('Картинка'),
        upload_to='recipes',
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name=_('Ингредиенты'),
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('Название ингредиента'),
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=200
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(verbose_name=_('Количество'),)

    class Meta:
        verbose_name = _('Рецепт_Ингредиент')
        verbose_name_plural = _('Рецепты_Ингредиенты')
        ordering = ('id',)
