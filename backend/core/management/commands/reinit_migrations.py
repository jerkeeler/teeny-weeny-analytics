import os

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Reinits all migrations, squashing them down to one single migration. Should NEVER be run on production.'

    def handle(self, *args, **options):
        res = input('Are you sure you wish to re-gen all migrations? (y/N) ')
        if res.lower() != 'y':
            raise CommandError('Command aborted!')
        for root, dirs, files in os.walk('.'):
            if root.endswith('migrations'):
                self.stdout.write(self.style.NOTICE(f'Removing migrations from {root}'))
                for file in files:
                    if file != '__init__.py':
                        path = os.path.join(root, file)
                        os.remove(path)
        call_command('makemigrations')
        self.stdout.write(self.style.SUCCESS('Migrations successfully regenerated!'))
