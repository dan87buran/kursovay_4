from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    avatar = models.ImageField(
        _('avatar'),
        upload_to='users/avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )

    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )

    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        null=True
    )

    is_blocked = models.BooleanField(
        _('blocked'),
        default=False,
        help_text=_('Designates whether the user is blocked.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email