from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer


from .models import Participant
from .serializers import (
    RegisterSerializer,
    ParticipantSerializer,
    GenerateTicketSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        responses={
            201: inline_serializer(
                name="TransactionLink",
                fields={
                    "status": serializers.CharField(default="success"),
                    "link": serializers.URLField(default=""),
                },
            ),
            424: inline_serializer(
                name="TransactionFailed",
                fields={
                    "status": serializers.CharField(default="failed"),
                    "message": serializers.CharField(default="An error occurred"),
                },
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        callback_url = serializer.validated_data.get("callback_url")
        participant = serializer.save()
        link = participant.generate_payment_link(callback_url=callback_url)
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(
                response_data,
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )
        return Response(
            {"link": link, "status": "success"},
            status=status.HTTP_201_CREATED,
        )


class ParticipantAPIView(generics.RetrieveAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get_object(self):
        return generics.get_object_or_404(
            self.get_queryset(), transaction__reference=self.kwargs.get("reference")
        )

    @extend_schema(
        responses={
            200: ParticipantSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GenerateTicketPaymentAPIView(generics.GenericAPIView):
    serializer_class = GenerateTicketSerializer
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        callback_url = serializer.validated_data.get("callback_url")

        participant = get_object_or_404(Participant, user=request.user)
        if participant.has_paid:
            raise serializers.ValidationError("Payment already made")
        link = participant.generate_payment_link(callback_url=callback_url)
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
