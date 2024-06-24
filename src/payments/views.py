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
                    "status": serializers.CharField(),
                    "link": serializers.URLField(),
                },
            ),
            424: inline_serializer(
                name="TransactionFailed",
                fields={
                    "status": serializers.CharField(),
                    "message": serializers.CharField(),
                },
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        callback_url = serializer.validated_data.get("callback_url")
        transaction = serializer.create()

        title = "Partnership payment"
        link = transaction.generate_payment_link(title=title, callback_url=callback_url)
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)

        response_data = {"status": "success", "link": link}
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
            tx_ref = response_data.get("data").get("tx_ref").split("_")[1]
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
            201: inline_serializer(
                name="TransactionSuccess",
                fields={
                    "status": serializers.CharField(default="success"),
                    "message": serializers.CharField(
                        default="Transaction was successful"
                    ),
                },
            ),
            208: inline_serializer(
                name="TransactionAlreadyProcessed",
                fields={
                    "status": serializers.CharField(default="success"),
                    "message": serializers.CharField(
                        default="Transaction already processed"
                    ),
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

        if response_data.get("status") == "success":
            tx_ref = response_data.get("data").get("tx_ref").split("_")[1]
            amount = response_data.get("data").get("amount")
            currency = response_data.get("data").get("currency")
            tx_status = response_data.get("data").get("status").lower()

            trans_object = Transaction.objects.filter(reference=tx_ref)
            if trans_object.exists():
                trans_object = trans_object.first()
            else:
                trans_object = None

            if trans_object and not trans_object.is_success:
                if (
                    tx_status == "successful"
                    and currency == trans_object.currency
                    and amount == trans_object.amount
                ):
                    trans_object.is_success = True
                    trans_object.save()
                    return Response(
                        {"status": "success", "message": "Transaction was successful"},
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
                return Response(
                    {"status": "success", "message": "Transaction already processed"},
                    status=status.HTTP_208_ALREADY_REPORTED,
                )

        elif response_data.get("status") == "error":
            return Response(
                {"status": "error", "message": "Invalid Transaction ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )
