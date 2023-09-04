# recipes/models.py
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
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
    )
    author = models.ForeignKey(
        get_user_model(),
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
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name=_('Ссылка на картинку на сайте'),
        upload_to='rescipes/',
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
            ),
            MaxValueValidator(
                1440,
                'Время готовки не должно быть больше суток'
            )
        ],
        help_text='Введите время готовки (мин.)'
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True,
        db_index=True,
        editable=False
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
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=200,
        help_text='Введите единицы измерения'
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]


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
    amount = models.PositiveIntegerField(
        verbose_name=_('Количество'),
        validators=[
            MinValueValidator(
                1,
                'Количество не должно быть меньше 1'
            ),
            MaxValueValidator(
                100_000,
                'Количество не должно быть больше 100.000'
            )
        ],
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('id',)
        unique_together = ('recipe', 'ingredient')


class Favorite(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name=_('Пользователь'),
        help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
        related_query_name='favorites',
        verbose_name=_('Рецепт'),
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} >> {self.recipe}'


class ShoppingCart(models.Model):
    """ Модель корзины покупок """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Пользователь'),
        help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Рецепт'),
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = _('Корзина покупок')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} >> {self.recipe}'
