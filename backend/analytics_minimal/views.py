from datetime import timedelta
from typing import Any

from django.db.models import Avg, Count, Q, FloatField
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpRequest, JsonResponse, Http404
from django.utils import timezone
from django.views import View
from django.views.generic.base import TemplateView

from analytics_minimal.models import APIKey, PageView, Session, Site, Visitor
from analytics_minimal.utils import anonymize_ip, get_gif_response, get_hostname, get_browser

BAD_RESPONSE = JsonResponse({'error': 'Bad request'}, status=400)
BOT_NAMES = ['googlebot', 'slurp', 'twiceler', 'msnbot', 'kaloogabot', 'yodaobot', 'baiduspider', 'speedy spider',
             'dotbot', 'duckduckbot', 'baidu', 'bingbot']


class V1Collect(View):
    def _convert_to_page_view(self, request: HttpRequest, api_key: APIKey) -> PageView:
        query_params = request.GET
        field_map = PageView.fields_to_query()

        page_view = PageView()
        page_view.event_id = query_params.get(field_map['event_id'])
        page_view.event_name = query_params.get(field_map['event_name'])
        page_view.previous_event_id = query_params.get(field_map['previous_event_id'])
        page_view.hostname = query_params.get(field_map['hostname'])
        page_view.path = query_params.get(field_map['path'])
        page_view.browser = query_params.get(field_map['browser'])
        page_view.page_load_time = query_params.get(field_map['page_load_time'])
        page_view.is_new_session = query_params.get(field_map['is_new_session'], False)
        page_view.is_new_user = query_params.get(field_map['is_new_user'], False)
        page_view.referrer = query_params.get(field_map['referrer'])
        page_view.screen_height = query_params.get(field_map['screen_height'])
        page_view.screen_width = query_params.get(field_map['screen_width'])
        page_view.api_key = api_key
        page_view.site = api_key.site

        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip:
            page_view.ip = anonymize_ip(ip)

        referrer = query_params.get(field_map['referrer'])
        if referrer:
            page_view.referrer = get_hostname(referrer)

        browser = query_params.get(field_map['browser'])
        if browser:
            page_view.browser = get_browser(browser)

        page_view.raw_request = request.build_absolute_uri()
        page_view.save()
        return page_view

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.META.get('DNT', '0') == '1':
            # Should never get here because JS shouldn't send GET request in the first place if DNT
            return get_gif_response()

        # Don't want to track any bots!
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(filter(lambda bot_name: bot_name in ua, BOT_NAMES)):
            return get_gif_response()

        query_params = request.GET
        field_map = PageView.fields_to_query()
        api_key = query_params.get(field_map['api_key'])
        hostname = query_params.get(field_map['hostname'])

        try:
            norm_hostname = hostname.replace('http://', '').replace('https://', '')
            actual_key = APIKey.objects.get(site__hostname=norm_hostname, active=True)
        except APIKey.DoesNotExist:
            return BAD_RESPONSE
        except AttributeError:
            # hostname is not provided
            return BAD_RESPONSE

        if api_key != actual_key.token:
            return BAD_RESPONSE

        event_id = query_params.get(field_map['event_id'])
        event_name = query_params.get(field_map['event_name'])
        path = query_params.get(field_map['path'])

        if any([x is None for x in [event_id, event_name, hostname, path]]):
            return BAD_RESPONSE

        page_view = self._convert_to_page_view(request, actual_key)
        # Get the new page view from DB so input objects are correctly coerced to their respective formats
        page_view = PageView.objects.get(token=page_view.token)
        visitor, session, previous_session, previous_view = None, None, None, None

        if page_view.previous_event_id:
            try:
                previous_view = PageView.objects.get(api_key=actual_key, event_id=page_view.previous_event_id)
                previous_view.next_event_id = page_view.event_id
            except PageView.DoesNotExist:
                print('Previous page view does not exist!')
            except PageView.MultipleObjectsReturned:
                print('Multiple page views with the previous id!')
                previous_view = (PageView.objects.filter(api_key=actual_key, event_id=page_view.previous_event_id)
                                 .order_by('-created_at').first())
                previous_view.next_event_id = page_view.event_id

        if previous_view and not page_view.is_new_session:
            previous_view.is_bounce = False
            previous_view.duration = page_view.created_at - previous_view.created_at

        if previous_view:
            previous_view.save()

        if previous_view and page_view.is_new_session:
            try:
                previous_session = Session.objects.get(site=page_view.site, last_page_view=previous_view)
                previous_session.active = False
                previous_session.duration = (previous_session.last_page_view.created_at -
                                             previous_session.first_page_view.created_at)

                previous_session.save()
            except Session.DoesNotExist:
                print('Previous session does not exist!')
            except Session.MultipleObjectsReturned:
                print('Multiple sessions with the same last page view!')
                previous_session = (Session.objects.filter(site=page_view.site, last_page_view=previous_view)
                                    .order_by('-created_at').first())
                previous_session.active = False
                previous_session.duration = (previous_session.last_page_view.created_at -
                                             previous_session.first_page_view.created_at)

                previous_session.save()

        if page_view.is_new_session:
            session = Session.objects.create(active=True, site=page_view.site, first_page_view=page_view,
                                             last_page_view=page_view)
        elif previous_view:
            try:
                session = Session.objects.get(site=page_view.site, last_page_view=previous_view)
                session.last_page_view = page_view
            except Session.DoesNotExist:
                print('Previous session does not exist!')
            except Session.MultipleObjectsReturned:
                print('Multiple sessions with the same last page view!')

        if page_view.is_new_user:
            visitor = Visitor.objects.create(site=page_view.site)
        elif previous_session or session:
            visitor = (previous_session and previous_session.visitor) or (session and session.visitor)

        if page_view.is_new_user and session:
            session.first_session = True

        if visitor and session and session.visitor is None:
            session.visitor = visitor

        if session:
            session.save()

        if not visitor:
            visitor = Visitor.objects.create(site=page_view.site)

        if not session:
            session = Session.objects.create(active=True, site=page_view.site, first_page_view=page_view,
                                             last_page_view=page_view, visitor=visitor)
        page_view.session = session
        page_view.save()

        return get_gif_response()


class Sandbox(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return get_gif_response()


class SiteView(TemplateView):
    template_name = 'site.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = Site.objects.get(hostname=kwargs.get('hostname'))
        context['site'] = site
        context['site_stats']= {
            'bounce_rate': round((PageView.objects.filter(site=site, is_bounce=True).count() /
                                  PageView.objects.filter(site=site).count()) * 100, 2),
            'uniques': Visitor.objects.filter(site=site).count(),
            'sessions': Session.objects.filter(site=site).count(),
            'total': PageView.objects.filter(site=site).count(),
            'duration': PageView.objects.filter(site=site).all().aggregate(Avg('duration'))['duration__avg'],
            'session_duration': Session.objects.filter(site=site).all().aggregate(Avg('duration'))['duration__avg'],
        }
        paths = PageView.objects.values('path').filter(site=site).annotate(pcount=Count('path'))
        path_data = {}
        for path in paths:
            path_stats = PageView.objects.filter(site=site, path=path['path']).aggregate(
                views=Count('token'),
                avg_duration=Avg('duration'),
                bounce_rate=(Cast(Count('token', filter=Q(is_bounce=True)), FloatField()) /
                             Cast(Count('token'), FloatField())) * 100,
            )
            unique_views = (Visitor.objects.values('token', 'session__pageview__path')
                            .filter(site=site, session__pageview__path=path['path']))
            uniques = set()
            for view in unique_views:
                uniques.add(view['token'])

            path_stats['unique_page_views'] = len(uniques)
            path_stats['path'] = path['path']
            path_data[path['path']] = path_stats
        data = [value for key, value in path_data.items()]
        data = sorted(data, key=lambda x: x['unique_page_views'], reverse=True)
        context['page_stats'] = data

        screens = (PageView.objects.values('screen_height', 'screen_width').filter(site=site)
                   .annotate(tcount=Count('token')).order_by('-tcount'))
        screen_data = {}
        for screen in screens:
            screen_tuple = (screen['screen_width'], screen['screen_height'],)
            screen_data[screen_tuple] = screen
            unique_screens = (Visitor.objects.values('token')
                              .filter(site=site, session__pageview__screen_width=screen_tuple[0],
                                      session__pageview__screen_height=screen_tuple[1]))
            uniques = set()
            for un in unique_screens:
                uniques.add(un['token'])

            screen['unique_occurrences'] = len(uniques)
            screen_data[screen_tuple] = screen

        screen_data = [value for key, value in screen_data.items()]
        screens = sorted(screen_data, key=lambda x: x['unique_occurrences'], reverse=True)
        context['screen_stats'] = screens

        browsers = (PageView.objects.values('browser').filter(site=site)
                    .annotate(tcount=Count('token')).order_by('-tcount'))
        browser_data = {}
        for browser in browsers:
            browser_data[browser['browser']] = browser
            unique_browsers = (Visitor.objects.values('token')
                               .filter(site=site, session__pageview__browser=browser['browser']))
            uniques = set()
            for un in unique_browsers:
                uniques.add(un['token'])

            browser['unique_occurrences'] = len(uniques)
            browser_data[browser['browser']] = browser

        browser_data = [value for key, value in browser_data.items()]
        browsers = sorted(browser_data, key=lambda x: x['unique_occurrences'], reverse=True)
        context['browser_stats'] = browsers

        referrers = (PageView.objects.values('referrer').filter(site=site)
                     .exclude(referrer='')
                     .exclude(referrer=None)
                     .annotate(tcount=Count('token')).order_by('-tcount'))
        context['referrer_stats'] = referrers

        mins_ago = timezone.now() - timedelta(minutes=15)
        context['current_visitors'] = Visitor.objects.filter(session__active=True, site=site,
                                                             session__last_page_view__created_at__gte=mins_ago).count()
        return context
