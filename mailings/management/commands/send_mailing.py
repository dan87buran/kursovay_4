from django.core.management.base import BaseCommand
from mailings.services import send_mailing_command


class Command(BaseCommand):
    help = 'Отправляет рассылку'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        success, message = send_mailing_command(mailing_id)

        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))