from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Модель User"""
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
    role = models.CharField(
        verbose_name=_('Роль пользователя'),
        max_length=32,
        default=USER,
        choices=CHOICES_ROLE
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


class Follower(models.Model):
    """Модель подписчиков"""
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )
