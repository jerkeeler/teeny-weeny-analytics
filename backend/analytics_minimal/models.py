from typing import Dict

from django.db import models

from core.consts import VARCHAR_LENGTH
from core.models import CreatedByMixin, TimeStampModel, TokenMixin


class Site(TimeStampModel, CreatedByMixin, TokenMixin):
    hostname: str = models.CharField(max_length=VARCHAR_LENGTH)

    def __str__(self) -> str:
        return self.hostname


class APIKey(TimeStampModel, CreatedByMixin, TokenMixin):
    active: bool = models.BooleanField(default=True)
    site: Site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self) -> str:
        return self.token


class PageView(TimeStampModel, TokenMixin):
    """
    JSON Payload equivalent:
    {
        eid: event_id,
        pid: preveious_event_id,
        h: hostname,
        p: path,
        r: referrer,
        b: browser
        nu: is_new_user,
        ns: is_new_session,
        sh: screen_height,
        sw: screen_width,
        ak: api_key
    }
    or address equivalent:
    collect?eid=event_id&pid=previous_event_id&h=hostname&p=path&r=referrer&
    b=browser&nu=is_new_user&ns=is_new_session&sh=screen_height&sw=screen_width&
    ak=api_key
    """
    event_id: str = models.CharField(max_length=VARCHAR_LENGTH)
    event_name: str = models.CharField(max_length=VARCHAR_LENGTH)
    previous_event_id: str = models.CharField(
        max_length=VARCHAR_LENGTH,
        null=True,
        blank=True,
    )

    hostname: str = models.CharField(max_length=VARCHAR_LENGTH)
    path: str = models.CharField(max_length=VARCHAR_LENGTH)

    browser: str = models.CharField(max_length=VARCHAR_LENGTH, null=True,
                                    blank=True)
    duration: float = models.DurationField(null=True, blank=True)
    # IP is anonymize when stored to drop last 80 bits
    ip: str = models.GenericIPAddressField(null=True, blank=True)
    is_bounce: bool = models.BooleanField(default=True)
    is_new_session: bool = models.BooleanField(default=False)
    is_new_user: bool = models.BooleanField(default=False)
    page_load_time: float = models.FloatField(null=True, blank=True)
    referrer: str = models.CharField(max_length=VARCHAR_LENGTH, null=True,
                                     blank=True)
    screen_height: int = models.IntegerField(null=True, blank=True)
    screen_width: int = models.IntegerField(null=True, blank=True)

    api_key: APIKey = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    site: Site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    raw_request: str = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.token

    @staticmethod
    def fields_to_query() -> Dict[str, str]:
        return {
            'event_id': 'eid',
            'event_name': 'en',
            'previous_event_id': 'pid',

            'hostname': 'h',
            'path': 'p',
            'browser': 'b',
            'page_load_time': 'lt',
            'is_new_session': 'ns',
            'is_new_user': 'nu',
            'referrer': 'r',
            'screen_height': 'sh',
            'screen_width': 'sw',

            'api_key': 'ak',
        }
