from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analytics_minimal.models import PageView, Visitor, Session


class Command(BaseCommand):
    help = 'Backfill pageviews that do not have Visitors and create those that do.'

    def handle(self, *args, **options):
        starts = PageView.objects.filter(is_new_user=True, session=None)
        self.stdout.write(self.style.SUCCESS(f'Creating {starts.count()} new Visitors!'))

        res = input('Are you sure you wish to backfill Visitors (y/N) ')
        if res.lower() != 'y':
            raise CommandError('Command aborted!')

        def get_next_page_view(previous_event_id):
            page_views = PageView.objects.filter(previous_event_id=previous_event_id)
            if page_views.count() == 0:
                return None

            if page_views.count() == 1:
                return page_views.first()

            # find the "most correct" page view out of possible
            event_ids = page_views.values('event_id').all()
            nexts = PageView.objects.filter(previous_event_id__in=event_ids)

            if nexts.count() == 0:
                return page_views.order_by('-created_at').first()

            if nexts.count() == 1:
                return page_views.filter(event_id=nexts.first().previous_event_id).first()

            return page_views.filter(event_id=nexts.first().previous_event_id).order_by('-created_at').first()

        with transaction.atomic():
            for start in starts:
                visitor = Visitor.objects.create(site=start.site)
                session = Session.objects.create(first_session=True, visitor=visitor, site=start.site,
                                                 first_page_view=start, last_page_view=start, active=True)
                start.session = session
                start.save()
                previous_page_view = start
                previous_session = session
                next_page_view = get_next_page_view(start.event_id)

                while next_page_view is not None:
                    # Traverse the start chain
                    # Get next, if more than one just get a random first
                    previous_page_view.next_event_id = next_page_view.event_id
                    previous_page_view.save()
                    if next_page_view.is_new_session:
                        session = Session.objects.create(visitor=visitor, site=start.site,
                                                         first_page_view=next_page_view,
                                                         last_page_view=next_page_view, active=True)
                        previous_session.active = False
                        previous_session.duration = (previous_session.last_page_view.created_at -
                                                     previous_session.first_page_view.created_at)
                        previous_session.save()
                    else:
                        session.last_page_view = next_page_view
                        session.save()
                    next_page_view.session = session
                    next_page_view.save()
                    previous_page_view = next_page_view
                    next_page_view = get_next_page_view(previous_page_view.event_id)

        self.stdout.write(self.style.SUCCESS('Successfully backfilled Visitors'))
