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
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"${self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            reference = uuid4()
            qs = Transaction.objects.filter(reference=reference)
            while qs.exists():
                reference = uuid4()
                qs = Transaction.objects.filter(reference=reference)
            self.reference = reference
        super().save(*args, **kwargs)

    def generate_payment_link(self, title, callback_url=None):
        headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}
        data = {
            "tx_ref": f"Church_{str(self.reference)}",
            "amount": float(self.amount),
            "currency": self.currency,
            "redirect_url": callback_url if callback_url else "example.com",
            "customer": {
                "email": self.email,
            },
            "customizations": {
                "title": title,
                "logo": config("LOGO_URL"),
            },
        }

        url = f"{config('FLUTTERWAVE_BASE_URL')}/payments"

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data").get("link")
