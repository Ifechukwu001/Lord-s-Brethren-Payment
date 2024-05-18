from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Transaction
from .serializers import TransactionSerializer


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
        if transaction.for_ticket:
            title = "Payment for ticket"

        link = transaction.generate_payment_link(title=title)
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)
        response_data = {"status": "success", "link": link}

        return Response(response_data, status=status.HTTP_201_CREATED)
