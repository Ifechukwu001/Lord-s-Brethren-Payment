import requests
from logging import getLogger
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from core.env import config
from .models import Transaction
from .serializers import TransactionSerializer
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
        transaction = serializer.create()

        title = "Partnership payment"
        link = transaction.generate_payment_link(title=title)
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

        transaction_id = request.data.get("id")
        url = f"{config('FLUTTERWAVE_BASE_URL')}/transactions/{transaction_id}/verify"
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response_data.get("status") == "success":
            tx_ref = response_data.get("data").get("tx_ref").split("_")[1]
            amount = response_data.get("data").get("amount")
            currency = response_data.get("data").get("currency")
            tx_status = response_data.get("data").get("status")

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
