from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analytics_minimal.models import PageView
from analytics_minimal.utils import get_hostname


class Command(BaseCommand):
    help = 'Backfill referrers so that they have only hostnames.'

    def handle(self, *args, **options):
        referrers = PageView.objects.exclude(referrer=None)
        self.stdout.write(self.style.SUCCESS(f'Backfilling {referrers.count()} referrers!'))

        res = input('Are you sure you wish to backfill referrers (y/N) ')
        if res.lower() != 'y':
            raise CommandError('Command aborted!')

        with transaction.atomic():
            for referrer in referrers:
                referrer.referrer = get_hostname(referrer.referrer)
                referrer.save()

        self.stdout.write(self.style.SUCCESS('Successfully backfilled referrers'))
