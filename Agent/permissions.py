from rest_framework import permissions

from . import utils

class IsHomewiseUser(permissions.BasePermission):
    """
    Permission for homewise users
    checking for user authentication and increasing the token expiry time by 3 days
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated():
            access_token = request.META['HTTP_AUTHORIZATION'][7:]  # get access token from header
            utils.generate_or_update_oauth_token(request.user, access_token)
            return True
        return False