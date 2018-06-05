from . import models

from oauth2_provider.models import AccessToken

from random import randint
from datetime import datetime, timedelta

def generate_or_update_oauth_token(user, access_token):
    """
    Generates or update oauth token for logged in user.
    Whenever user is sending access_token in header token expiry time increases by 3 days
    usage in: account.permissions.IsHomewiseUser has_permission
    """
    try:
        data = {
            # 'application_id': settings.APPLICATION_ID,
            'expires': datetime.now() + timedelta(days=3),
            # 'token': access_token,
            # 'scope': ''
        }
        AccessToken.objects.update_or_create(token=access_token, defaults=data)
        return access_token
    except:
        return None