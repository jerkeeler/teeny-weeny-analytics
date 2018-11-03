from typing import Any

from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views import View

from analytics_minimal.models import APIKey, PageView
from analytics_minimal.utils import anonymize_ip, get_gif_response

BAD_RESPONSE = JsonResponse({'error': 'Bad request'}, status=400)
BOT_NAMES = ['googlebot', 'slurp', 'twiceler', 'msnbot', 'kaloogabot', 'yodaobot', 'baiduspider', 'speedy spider',
             'dotbot', 'duckduckbot', 'baidu', 'bingbot']


class Collect(View):
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

        page_view.ip = anonymize_ip(request.META.get('REMOTE_ADDR'))
        page_view.raw_request = request.build_absolute_uri()
        return page_view

    def _get_cache_key(self, request: HttpRequest, page_view: PageView) -> str:
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')
        return f'{ip}-{ua}-{page_view.api_key}-{page_view.hostname}-{page_view.path}-{page_view.event_name}'

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
        norm_hostname = hostname.replace('http://', '').replace('https://', '')

        try:
            actual_key = APIKey.objects.get(site__hostname=norm_hostname, active=True)
        except APIKey.DoesNotExist:
            return BAD_RESPONSE

        if api_key != actual_key.token:
            return BAD_RESPONSE

        event_id = query_params.get(field_map['event_id'])
        event_name = query_params.get(field_map['event_name'])
        path = query_params.get(field_map['path'])

        if any([x is None for x in [event_id, event_name, hostname, path]]):
            return BAD_RESPONSE

        page_view = self._convert_to_page_view(request, actual_key)

        # # Prevents user from tracking on the same page with the same event name more than once every 1 seconds
        # # 1 seconds is defined in default cache time
        # cache_key = self._get_cache_key(request, page_view)
        # if cache.get(cache_key):
        #     return SUCCESS

        page_view.save()
        # Get the new page view from DB so input objects are correctly coerced to their respective formats
        page_view = PageView.objects.get(token=page_view.token)

        if (not page_view.is_new_session) and page_view.previous_event_id:
            try:
                previous_view = PageView.objects.get(api_key=actual_key, event_id=page_view.previous_event_id)
            except PageView.DoesNotExist:
                print('Previous page view does not exist!')
                return get_gif_response()
            previous_view.is_bounce = False
            previous_view.duration = page_view.created_at - previous_view.created_at
            previous_view.save()

        return get_gif_response()


class Sandbox(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return get_gif_response()
