# recipes/models.py
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        verbose_name=_('Название тега'),
        max_length=200,
    )
    color = models.CharField(
        verbose_name=_('HEX-цвет тега'),
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Список тегов'),
        help_text='Выставите теги',
        related_name='tags'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name=_('Автор рецепта'),
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name=_('Список ингредиентов'),
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        help_text='Выберете ингредиенты'
    )
    is_favorited = models.BooleanField(
        verbose_name=_('Добавить в избранное'),
        blank=True, default=False
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name=_('Добавить в покупки'),
        blank=True, default=False
    )
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name=_('Ссылка на картинку на сайте'),
        upload_to='recipes',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )
    text = models.CharField(
        verbose_name=_('Описание'),
        max_length=250,
        help_text='Составьте описание'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('Время приготовления (в минутах)'),
        validators=[
            MinValueValidator(
                1,
                'Время готовки не должно быть меньше минуты'
            )
        ],
        help_text='Введите время готовки (мин.)'
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        verbose_name=_('Название ингредиента'),
        max_length=200,
        help_text=''
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=200,
        help_text=''
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)


class RecipeIngredient(models.Model):
    """Модель рецепты_ингредиенты"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(verbose_name=_('Количество'),)

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)
