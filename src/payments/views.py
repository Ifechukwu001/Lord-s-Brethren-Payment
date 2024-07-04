import requests
from logging import getLogger
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from core.env import config
from .models import Transaction
from .serializers import TransactionSerializer, TransactionVerifySerializer
from .processing import payment_queue

logger = getLogger("Transaction")


class TransactionCreateView(generics.GenericAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            201: inline_serializer(
                name="TransactionLink",
                fields={
                    "status": serializers.CharField(default="success"),
                    "link": serializers.URLField(default=""),
                    "reference": serializers.CharField(default=""),
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        callback_url = serializer.validated_data.get("callback_url")
        transaction = serializer.create()

        description = "Partner with us to make the conference a success"
        link, reference = transaction.generate_payment_link(
            description=description, callback_url=callback_url
        )
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)

        response_data = {"status": "success", "link": link, "reference": reference}
        return Response(response_data, status=status.HTTP_201_CREATED)


class TransactionWebHook(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(exclude=True)
    def post(self, request, *args, **kwargs):
        hook_hash = config("FLUTTERWAVE_WEBHOOK_HASH")
        signature = request.headers.get("verif-hash")
        if not signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if signature != hook_hash:
            return Response(status=status.HTTP_403_FORBIDDEN)

        logger.info(request.data)
        print(request.data)

        transaction_id = request.data.get("id")
        url = f"{config('FLUTTERWAVE_BASE_URL')}/transactions/{transaction_id}/verify"
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response_data.get("status") == "success":
            tx_ref = response_data.get("data").get("tx_ref")
            amount = response_data.get("data").get("amount")
            currency = response_data.get("data").get("currency")
            tx_status = response_data.get("data").get("status").lower()

            transaction = {
                "tx_ref": tx_ref,
                "amount": amount,
                "currency": currency,
                "status": tx_status,
            }

            payment_queue.put(transaction)

        elif response_data.get("status") == "error":
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)


class TransactionVerifyAPIView(generics.GenericAPIView):
    serializer_class = TransactionVerifySerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="TransactionSuccess",
                fields={
                    "status": serializers.CharField(default="success"),
                    "message": serializers.CharField(
                        default="Transaction was successful"
                    ),
                    "details": serializers.DictField(default={}),
                    "group": serializers.CharField(default="participant"),
                },
            ),
            208: inline_serializer(
                name="TransactionAlreadyProcessed",
                fields={
                    "status": serializers.CharField(default="success"),
                    "message": serializers.CharField(
                        default="Transaction already processed"
                    ),
                    "details": serializers.DictField(default={}),
                    "group": serializers.CharField(default="participant"),
                },
            ),
            400: inline_serializer(
                name="TransactionIDWrong",
                fields={
                    "status": serializers.CharField(default="error"),
                    "message": serializers.CharField(default="Invalid Transaction ID"),
                },
            ),
            424: inline_serializer(
                name="TransactionCanceled",
                fields={
                    "status": serializers.CharField(default="failed"),
                    "message": serializers.CharField(
                        default="Transaction was not successful"
                    ),
                },
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction_id = serializer.validated_data.get("transaction_id")
        url = f"{config('FLUTTERWAVE_BASE_URL')}/transactions/{transaction_id}/verify"
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}

        response = requests.get(url, headers=headers)
        response_data = response.json()

        print(response_data)

        if response_data.get("status") == "success":
            tx_ref = response_data.get("data").get("tx_ref")
            amount = response_data.get("data").get("amount")
            currency = response_data.get("data").get("currency")
            tx_status = response_data.get("data").get("status").lower()

            trans_object = Transaction.objects.filter(reference=tx_ref)
            if trans_object.exists():
                trans_object = trans_object.first()
            else:
                trans_object = None

            if trans_object:
                if not trans_object.is_success:
                    if (
                        tx_status == "successful"
                        and currency == trans_object.currency
                        and amount == trans_object.amount
                    ):
                        trans_object.is_success = True
                        trans_object.save()

                        details = {
                            "reference": tx_ref,
                            "amount": amount,
                        }
                        group = None
                        try:
                            p = trans_object.participant
                            details.update(
                                {
                                    "firstname": p.firstname,
                                    "lastname": p.lastname,
                                    "email": p.email,
                                    "phone": p.phone,
                                    "category": p.category,
                                    "gender": p.gender,
                                }
                            )
                            group = "participant"
                        except Transaction.participant.RelatedObjectDoesNotExist:
                            pass

                        try:
                            pt = trans_object.partner
                            details.update(
                                {
                                    "email": pt.email,
                                    "name": pt.name,
                                    "phone": pt.phone,
                                    "country": pt.country,
                                }
                            )
                            group = "partner"
                        except Transaction.partner.RelatedObjectDoesNotExist:
                            pass

                        return Response(
                            {
                                "status": "success",
                                "message": "Transaction was successful",
                                "details": details,
                                "group": group,
                            },
                            status=status.HTTP_200_OK,
                        )
                    if tx_status == "failed":
                        return Response(
                            {
                                "status": "failed",
                                "message": "Transaction was not successful",
                            },
                            status=status.HTTP_402_PAYMENT_REQUIRED,
                        )
                else:
                    details = {
                        "reference": tx_ref,
                        "amount": amount,
                    }
                    group = None
                    try:
                        p = trans_object.participant
                        details.update(
                            {
                                "firstname": p.firstname,
                                "lastname": p.lastname,
                                "email": p.email,
                                "phone": p.phone,
                                "category": p.category,
                                "gender": p.gender,
                            }
                        )
                        group = "participant"
                    except Transaction.participant.RelatedObjectDoesNotExist:
                        pass

                    try:
                        pt = trans_object.partner
                        details.update(
                            {
                                "email": pt.email,
                                "name": pt.name,
                                "phone": pt.phone,
                                "country": pt.country,
                            }
                        )
                        group = "partner"
                    except Transaction.partner.RelatedObjectDoesNotExist:
                        pass

                    return Response(
                        {
                            "status": "success",
                            "message": "Transaction already processed",
                            "details": details,
                            "group": group,
                        },
                        status=status.HTTP_208_ALREADY_REPORTED,
                    )

            return Response(
                {"status": "error", "message": "Invalid Transaction"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif response_data.get("status") == "error":
            return Response(
                {"status": "error", "message": "Invalid Transaction ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )
