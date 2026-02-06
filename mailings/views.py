from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView, CreateView, UpdateView,
    DeleteView, DetailView, TemplateView
)
from django.core.mail import send_mail
from django.conf import settings

from .models import Recipient, Message, Mailing, MailingAttempt

class OwnerRequiredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)


# Recipient Views
class RecipientListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.can_view_all_recipients'):
            return qs
        return qs.filter(owner=self.request.user)


class RecipientForm:
    pass


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientForm:
    pass


class RecipientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipient_list')


class RecipientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('recipient_list')


# Message Views (аналогично для Message)
# Mailing Views (аналогично для Mailing)

class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(mailing__owner=self.request.user)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            mailings = Mailing.objects.filter(owner=self.request.user)
            recipients = Recipient.objects.filter(owner=self.request.user)
        else:
            mailings = Mailing.objects.none()
            recipients = Recipient.objects.none()

        active_mailings = [
            mailing for mailing in mailings
            if mailing.is_active()
        ]

        context.update({
            'total_mailings': mailings.count(),
            'active_mailings': len(active_mailings),
            'unique_recipients': recipients.count(),
        })

        return context


def cache_page(param):
    pass


@method_decorator(cache_page(60 * 5), name='dispatch')  # Кешировать на 5 минут
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, cache=None, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ключ для кеша
        cache_key = f'home_stats_{self.request.user.id if self.request.user.is_authenticated else "anonymous"}'

        if cache.get(cache_key):
            return cache.get(cache_key)

        # ... логика получения данных ...

        cache.set(cache_key, context, 300)  # Кешировать на 5 минут
        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            # Для менеджеров - все рассылки
            mailings = Mailing.objects.all()
            attempts = MailingAttempt.objects.all()
        else:
            # Для пользователей - только свои
            mailings = Mailing.objects.filter(owner=self.request.user)
            attempts = MailingAttempt.objects.filter(mailing__owner=self.request.user)

        # Статистика по попыткам
        total_attempts = attempts.count()
        successful_attempts = attempts.filter(status=MailingAttempt.SUCCESS).count()
        failed_attempts = attempts.filter(status=MailingAttempt.FAILED).count()

        # Статистика по рассылкам
        mailing_stats = []
        for mailing in mailings:
            mailing_attempts = attempts.filter(mailing=mailing)
            mailing_stats.append({
                'mailing': mailing,
                'total': mailing_attempts.count(),
                'success': mailing_attempts.filter(status=MailingAttempt.SUCCESS).count(),
                'failed': mailing_attempts.filter(status=MailingAttempt.FAILED).count(),
            })

        context.update({
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'mailing_stats': mailing_stats,
        })

        return context