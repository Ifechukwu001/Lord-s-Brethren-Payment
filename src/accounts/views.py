from dj_rest_auth.views import LoginView as DJLoginView, LogoutView as DjLogoutView
from rest_framework import serializers, exceptions
from drf_spectacular.utils import extend_schema, inline_serializer


class LoginView(DJLoginView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.

    Accept the following POST parameters: email, password and
    return the JWT access and refresh tokens.
    """

    pass


class LogoutView(DjLogoutView):
    """
    Logs out a user and deletes the JWT token.

    Accepts the following POST parameters: refresh_token"""

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=inline_serializer(
            "Logout",
            {"refresh": serializers.CharField(required=True)},
        )
    )
    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if not refresh:
            raise exceptions.ValidationError("Refresh token is required")
        return super().post(request, *args, **kwargs)
