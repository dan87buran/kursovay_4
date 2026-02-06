from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(_('email'), unique=True)
    full_name = models.CharField(_('full name'), max_length=255)
    comment = models.TextField(_('comment'), blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name=_('owner')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('recipient')
        verbose_name_plural = _('recipients')
        ordering = ['-created_at']
        permissions = [
            ('can_view_all_recipients', 'Can view all recipients'),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('owner')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-created_at']
        permissions = [
            ('can_view_all_messages', 'Can view all messages'),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    CREATED = 'Создана'
    STARTED = 'Запущена'
    COMPLETED = 'Завершена'

    STATUS_CHOICES = [
        (CREATED, _('Created')),
        (STARTED, _('Started')),
        (COMPLETED, _('Completed')),
    ]

    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name=_('message')
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name=_('recipients')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name=_('owner')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('mailing')
        verbose_name_plural = _('mailings')
        ordering = ['-created_at']
        permissions = [
            ('can_view_all_mailings', 'Can view all mailings'),
            ('can_disable_mailing', 'Can disable mailing'),
        ]

    def __str__(self):
        return f'Рассылка {self.id} ({self.get_status_display()})'

    def update_status(self):
        now = timezone.now()

        if now < self.start_time:
            new_status = self.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STARTED
        else:
            new_status = self.COMPLETED

        return new_status

    @property
    def status(self):
        return self.update_status()

    def is_active(self):
        return self.status == self.STARTED


class MailingAttempt(models.Model):
    SUCCESS = 'Успешно'
    FAILED = 'Не успешно'

    STATUS_CHOICES = [
        (SUCCESS, _('Success')),
        (FAILED, _('Failed')),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('mailing')
    )
    attempt_time = models.DateTimeField(_('attempt time'), auto_now_add=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES
    )
    server_response = models.TextField(_('server response'), blank=True)

    class Meta:
        verbose_name = _('mailing attempt')
        verbose_name_plural = _('mailing attempts')
        ordering = ['-attempt_time']

    def __str__(self):
        return f'Попытка {self.id} ({self.status})'
