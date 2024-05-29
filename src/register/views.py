from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from dj_rest_auth.registration.views import RegisterView as DJRegisterView


from .models import Participant
from .serializers import ParticipantSerializer


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


class ParticipantAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParticipantSerializer

    def get_object(self):
        return get_object_or_404(Participant, user=self.request.user)

    @extend_schema(
        responses={
            200: ParticipantSerializer,
        }
    )
    def get(self, request):
        return super().get(request)

    @extend_schema(
        responses={
            200: ParticipantSerializer,
        }
    )
    def put(self, request):
        return super().patch(request)


class GenerateTicketPaymentAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            201: inline_serializer(
                name="GenerateTicketPaymentResponse",
                fields={
                    "link": serializers.URLField(),
                    "message": serializers.CharField(),
                },
            ),
        }
    )
    def post(self, request):
        participant = get_object_or_404(Participant, user=request.user)
        if participant.has_paid:
            raise serializers.ValidationError("Payment already made")
        link = participant.generate_payment_link()
        if not link:
            return Response(
                {
                    "message": "Payment link could not be generated",
                },
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )
        return Response(
            {
                "link": link,
                "message": "Payment link generated successfully",
            },
            status=status.HTTP_201_CREATED,
        )
