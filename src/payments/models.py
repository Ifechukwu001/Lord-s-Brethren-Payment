from uuid import uuid4
import requests
from django.db import models

from core.env import config


class Transaction(models.Model):
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    reference = models.CharField(max_length=20, editable=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"$__{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            reference = uuid4().hex[:10]
            qs = Transaction.objects.filter(reference=reference)
            while qs.exists():
                reference = uuid4().hex[:10]
                qs = Transaction.objects.filter(reference=reference)
            self.reference = reference
        super().save(*args, **kwargs)

    def generate_payment_link(self, description, callback_url=None):
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}
        callback = (
            callback_url
            if callback_url
            else config("PAYMENT_REDIRECT_URL", default="") or "http://example.com"
        )
        data = {
            "tx_ref": self.reference,
            "amount": float(self.amount),
            "currency": self.currency,
            "redirect_url": callback,
            "customer": {
                "email": self.email,
            },
            "customizations": {
                "title": "The Lord's Brethren Convocation 2024 (TLBC'24)",
                "description": description,
                "logo": config("LOGO_URL"),
            },
        }

        url = f"{config('FLUTTERWAVE_BASE_URL')}/payments"

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data").get("link")
