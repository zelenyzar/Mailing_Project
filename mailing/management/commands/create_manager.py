# user/management/commands/create_manager.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class Command(BaseCommand):
    help = "Создает менеджера: дает доступ в админку, добавляет в группу и выдает права по ключевым словам."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email пользователя (будет логином)')
        parser.add_argument('--password', type=str, default='password123', help='Пароль пользователя')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        # 1. Работа с группой
        group, created = Group.objects.get_or_create(name='manager')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "manager" создана.'))
        else:
            self.stdout.write('Группа "manager" уже существует.')

        # 2. Работа с пользователем
        user, user_created = User.objects.get_or_create(email=email)

        if user_created:
            # Если пользователь НОВЫЙ: ставим пароль и даем доступ в админку
            user.set_password(password)
            user.is_staff = True  # <--- ЭТО ГЛАВНОЕ: дает вход в /admin/
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Пользователь "{email}" создан с паролем "{password}".'))
            self.stdout.write(self.style.SUCCESS('Статус "Staff" (доступ в админку) включен.'))
        else:
            # Если пользователь СТАРЫЙ: НЕ меняем пароль (безопасность),
            # но принудительно включаем доступ в админку, если его вдруг нет
            if not user.is_staff:
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.WARNING(f'⚠️ Пользователь "{email}" уже существует. Пароль не изменён.'))
                self.stdout.write(self.style.SUCCESS('Статус "Staff" (доступ в админку) принудительно включен.'))
            else:
                self.stdout.write(f'Пользователь "{email}" уже существует. Пароль и статус не изменены.')

        # 3. Добавляем в группу
        if not user.groups.filter(name='manager').exists():
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'Пользователь "{email}" добавлен в группу "manager".'))
        else:
            self.stdout.write(f'Пользователь "{email}" уже состоит в группе "manager".')

        # 4. АВТОМАТИЧЕСКИЙ ПОИСК И НАЗНАЧЕНИЕ ПРАВ
        keywords = [
            'user', 'пользователь',
            'client', 'клиент',
            'recipient', 'получатель',
            'mail', 'рассылка',
        ]

        found_permissions = set()
        self.stdout.write('\n🔍 Начинаю поиск подходящих прав...')

        for keyword in keywords:
            perms = Permission.objects.filter(name__icontains=keyword)
            if perms.exists():
                count = perms.count()
                self.stdout.write(f"   Найдено {count} прав по ключевому слову '{keyword}':")
                for p in perms:
                    self.stdout.write(f"      - {p.name} ({p.codename})")
                    found_permissions.add(p)

        if found_permissions:
            user.user_permissions.add(*found_permissions)
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Автоматически выдано {len(found_permissions)} прав пользователю "{email}".'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️ Не найдено ни одного подходящего права по ключевым словам!'))

        self.stdout.write('\n🏁 Готово! Теперь пользователь может войти в админку.')
