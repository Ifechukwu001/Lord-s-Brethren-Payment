from uuid import uuid4
import requests
from django.db import models

from core.env import config


class Transaction(models.Model):
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    reference = models.UUIDField(default=uuid4, editable=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    for_ticket = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"${self.reference}"

    def generate_payment_link(self, title):
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}
        data = {
            "tx_ref": f"Church_{str(self.reference)}",
            "amount": float(self.amount),
            "currency": self.currency,
            "redirect_url": config("PAYMENT_REDIRECT_URL"),
            "customer": {
                "email": self.email,
            },
            "customizations": {
                "title": "Payment for services",
                "logo": config("LOGO_URL"),
            },
        }

        url = f"{config('FLUTTERWAVE_BASE_URL')}/payments"

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data").get("link")
