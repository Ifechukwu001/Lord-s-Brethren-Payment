from dj_rest_auth.serializers import (
    JWTSerializer as DJJWTSerializer,
    LoginSerializer as DJLoginSerializer,
)


class JWTSerializer(DJJWTSerializer):
    user = None


class LoginSerializer(DJLoginSerializer):
    username = None
