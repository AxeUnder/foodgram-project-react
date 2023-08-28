# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Модель переопределенного пользователя"""
    USER = 'user'
    ADMIN = 'admin'

    CHOICES_ROLE = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    )

    username = models.CharField(
        verbose_name=_('Логин'),
        max_length=150,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=254,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        verbose_name=_('Имя'),
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name=_('Фамилия'),
        max_length=150,
        blank=False
    )
    is_subscribed = models.BooleanField(
        verbose_name=_('Подписаться на автора'),
        blank=True,
        default=False,
    )
    password = models.CharField(
        verbose_name=_('Пароль'),
        max_length=150,
        blank=False,
    )
    role = models.CharField(
        verbose_name=_('Роль пользователя'),
        max_length=32,
        default=USER,
        choices=CHOICES_ROLE
    )
    following = models.ManyToManyField(
        "self",
        through='Subscription',
        through_fields=('user', 'author'),
        symmetrical=False,
        related_name='following_relationships'
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('id',)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(
        CustomUser,
        verbose_name=_('Подписчик'),
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    class Meta:
        verbose_name = _('Подписчик')
        verbose_name_plural = _('Подписчики')
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscripting'
            ),
        ]

    def __str__(self):
        return f'{self.user} >> {self.author}'
