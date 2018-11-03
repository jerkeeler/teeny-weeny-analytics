from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from core import utils, consts


class CreatedByMixin(models.Model):
    created_by: User = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        editable=False,
        blank=True,
        null=True,
        related_name='%(app_label)s_%(class)s_creator_related',
        related_query_name='%(app_label)s_%(class)ss_creator',
    )
    updated_by: User = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        editable=False,
        blank=True,
        null=True,
        related_name='%(app_label)s_%(class)s_updater_related',
        related_query_name='%(app_label)s_%(class)ss_updater',
    )

    class Meta:
        abstract = True


class TimeStampModel(models.Model):
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TokenMixin(models.Model):
    token: str = models.CharField(
        max_length=consts.VARCHAR_LENGTH,
        default=utils.gen_token,
        blank=True,
        unique=True,
    )

    class Meta:
        abstract = True
