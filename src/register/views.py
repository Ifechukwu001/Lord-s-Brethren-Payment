from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer


from core.env import config
from .models import Participant, Partner
from .serializers import (
    ParticipantRegisterSerializer,
    PartnerRegisterSerializer,
    ParticipantSerializer,
    PartnerSerializer,
    SearchSerializer,
    GenerateSerializer,
)


class ParticipantRegisterView(generics.CreateAPIView):
    serializer_class = ParticipantRegisterSerializer

    @extend_schema(
        responses={
            201: inline_serializer(
                name="RegistrationLink",
                fields={
                    "status": serializers.CharField(default="success"),
                    "link": serializers.URLField(default=""),
                    "reference": serializers.CharField(default="TLBC240001"),
                    "amount": serializers.CharField(default="2000"),
                    "category": serializers.CharField(default="Invitee"),
                },
            ),
            424: inline_serializer(
                name="RegistrationFailed",
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
        link, _ = participant.generate_payment_link(callback_url=callback_url)
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(
                response_data,
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )

        if participant.category == Participant.Types.INVITEE:
            details = {"amount": config("INVITEE_PRICE"), "category": "Invitee"}
        else:
            details = {"amount": config("MEMBER_PRICE"), "category": "Member"}
        return Response(
            {
                "link": link,
                "status": "success",
                "reference": participant.reference,
                **details,
            },
            status=status.HTTP_201_CREATED,
        )


class PartnerRegisterView(generics.CreateAPIView):
    serializer_class = PartnerRegisterSerializer

    @extend_schema(
        responses={
            201: inline_serializer(
                name="RegistrationLink",
                fields={
                    "status": serializers.CharField(default="success"),
                    "link": serializers.URLField(default=""),
                    "reference": serializers.CharField(default="TLBC240001P"),
                },
            ),
            424: inline_serializer(
                name="RegistrationFailed",
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
        amount = serializer.validated_data.get("amount")
        currency = serializer.validated_data.get("currency")
        partner = serializer.save()
        link, _ = partner.generate_payment_link(
            amount, currency, callback_url=callback_url
        )
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(
                response_data,
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )

        return Response(
            {"link": link, "status": "success", "reference": partner.reference},
            status=status.HTTP_201_CREATED,
        )


class ParticipantAPIView(generics.RetrieveAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    lookup_field = "reference"

    @extend_schema(
        responses={
            200: ParticipantSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PartnerAPIView(generics.RetrieveAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    lookup_field = "reference"

    @extend_schema(
        responses={
            200: PartnerSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SearchAPIView(generics.ListAPIView):
    serializer_class = SearchSerializer

    def get(self, request, *args, **kwargs):
        email = self.kwargs.get("email")

        results = list()

        participants = Participant.objects.exclude(transaction__is_success=True).filter(
            email=email
        )
        if participants.exists():
            serializer = self.get_serializer(participants, many=True)
            results.extend(serializer.data)

        partners = Partner.objects.exclude(transaction__is_success=True).filter(
            email=email
        )
        if partners.exists():
            serializer = self.get_serializer(partners, many=True)
            results.extend(serializer.data)

        return Response(results, status=status.HTTP_200_OK)


class GeneratePaymentLinkAPIView(generics.GenericAPIView):
    serializer_class = GenerateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        callback_url = serializer.validated_data.get("callback_url")
        reference = serializer.validated_data.get("reference")

        if reference.endswith("P"):
            partner = get_object_or_404(Partner, reference=reference)
            link, _ = partner.generate_payment_link(callback_url=callback_url)
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
        else:
            participant = get_object_or_404(Participant, reference=reference)
            link, _ = participant.generate_payment_link(callback_url=callback_url)
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
