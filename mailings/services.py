from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingAttempt, Recipient


def send_mailing(mailing):
    """Отправка рассылки"""
    now = timezone.now()

    # Проверка времени
    if not (mailing.start_time <= now <= mailing.end_time):
        return False, 'Время рассылки неактивно'

    # Отправка каждому получателю
    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            # Запись успешной попытки
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.SUCCESS,
                server_response='Успешно отправлено'
            )

        except Exception as e:
            # Запись неуспешной попытки
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.FAILED,
                server_response=str(e)
            )

    return True, 'Рассылка отправлена'


def send_mailing_command(mailing_id):
    """Команда для отправки рассылки"""
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        success, message = send_mailing(mailing)
        return success, message
    except Mailing.DoesNotExist:
        return False, 'Рассылка не найдена'
