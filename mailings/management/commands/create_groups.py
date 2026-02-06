from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Recipient, Message, Mailing


class Command(BaseCommand):
    help = 'Создает группы с правами доступа'

    def handle(self, *args, **options):
        # Группа "Менеджеры"
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        # Получаем контент-тайпы
        recipient_ct = ContentType.objects.get_for_model(Recipient)
        message_ct = ContentType.objects.get_for_model(Message)
        mailing_ct = ContentType.objects.get_for_model(Mailing)

        # Права для менеджеров
        manager_permissions = [
            # Права на просмотр всех сущностей
            (recipient_ct, 'can_view_all_recipients'),
            (message_ct, 'can_view_all_messages'),
            (mailing_ct, 'can_view_all_mailings'),
            (mailing_ct, 'can_disable_mailing'),

            # Базовые права просмотра
            (recipient_ct, 'view_recipient'),
            (message_ct, 'view_message'),
            (mailing_ct, 'view_mailing'),
        ]

        for content_type, codename in manager_permissions:
            try:
                permission = Permission.objects.get(
                    content_type=content_type,
                    codename=codename
                )
                manager_group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Право {codename} не найдено')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Группа "{manager_group.name}" создана')
        )