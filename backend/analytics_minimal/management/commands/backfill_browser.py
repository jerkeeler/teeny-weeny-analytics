from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analytics_minimal.models import PageView
from analytics_minimal.utils import get_browser


class Command(BaseCommand):
    help = 'Backfill browsers so that they have only version and browser'

    def handle(self, *args, **options):
        browsers = PageView.objects.exclude(browser=None).exclude(browser='')
        self.stdout.write(self.style.SUCCESS(f'Backfilling {browsers.count()} browsers!'))

        res = input('Are you sure you wish to backfill browsers (y/N) ')
        if res.lower() != 'y':
            raise CommandError('Command aborted!')

        with transaction.atomic():
            for browser in browsers:
                browser.browser = get_browser(browser.browser)
                browser.save()

        self.stdout.write(self.style.SUCCESS('Successfully backfilled browsers'))
