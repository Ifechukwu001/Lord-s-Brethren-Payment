from decimal import Decimal
from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("1.00")
    )
    currency = serializers.CharField(max_length=3, default="NGN")
    email = serializers.EmailField()
    callback_url = serializers.URLField(required=False)

    def validate_currency(self, value):
        return value.upper()

    def create(self):
        validated_data = self.validated_data
        email = validated_data.get("email")
        amount = validated_data.get("amount")
        currency = validated_data.get("currency", "NGN")
        transaction = Transaction.objects.filter(
            email=email,
            is_success=False,
            amount=amount,
            currency=currency,
        )
        if transaction.exists():
            return transaction.first()
        return Transaction.objects.create(email=email, amount=amount, currency=currency)


class TransactionVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
