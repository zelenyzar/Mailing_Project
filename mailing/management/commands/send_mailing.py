from django.core.management import BaseCommand, CommandError
from mailing.models import Mailing

class Command(BaseCommand):
    help = 'Запускает указанную рассылку вручную'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена')
        self.stdout.write(f'Попытка запуска рассылки {mailing_id}...')
        success, errors = mailing.send()

        if success:
            self.stdout.write(self.style.SUCCESS(f'Рассылка #{mailing_id} успешно отправлена!'))
        else:
            self.stdout.write(self.style.ERROR(f'Частичная ошибка в рассылке #{mailing_id}: {errors}'))
            for err in errors:
                self.stdout.write(f' - {err}')
