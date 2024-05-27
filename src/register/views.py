from rest_framework import generics, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from dj_rest_auth.registration.views import RegisterView as DJRegisterView

from .serializers import RegisterSerializer


class RegisterView(DJRegisterView):
    @extend_schema(
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
        }
    )
    def post(self, request):
        return super().post(request)

    def get_response_data(self, user):
        data = super().get_response_data(user)
        if "user" in data:
            data.pop("user")
        return data
