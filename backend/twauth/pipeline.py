from twauth.models import UserProfile


def create_profile(backend, user, response, *args, **kwargs):
    try:
        user.userprofile
    except UserProfile.DoesNotExist:
        username = user.username
        if backend.name == 'github':
            username = response.get('name', user.username)
        elif backend.name == 'google-oauth2':
            username = response.get('displayName', user.username)
        profile = UserProfile(
            user=user,
            display_name=username,
            created_by=user,
            updated_by=user,
        )
        profile.save()
