from django.db import models
from core.models import CreatedByMixin, TimeStampModel, TokenMixin
from core import consts


class UserProfile(TimeStampModel, CreatedByMixin, TokenMixin):
    display_name = models.CharField(
        max_length=consts.VARCHAR_LENGTH,
    )
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
    )
    disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name
