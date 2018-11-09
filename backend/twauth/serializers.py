from rest_framework import serializers

from twauth.models import UserProfile


class UserProfileField(serializers.RelatedField):
    def to_representation(self, value):
        try:
            return {
                'display_name': value.userprofile.display_name,
                'token': value.userprofile.token,
            }
        except UserProfile.DoesNotExist:
            return None
