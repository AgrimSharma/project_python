from django.contrib.auth.models import User

from apps.avatar import AVATAR_DEFAULT_URL

def get_avatar(user):
    if not isinstance(user, User):
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return None
    avatars = user.avatar_set.order_by('-date_uploaded')
    primary = avatars.filter(primary=True)
    if primary.count() > 0:
        avatar = primary[0]
    elif avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    return avatar