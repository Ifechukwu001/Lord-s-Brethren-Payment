from django.conf import settings
from django.db import models


class Participant(models.Model):
    class Types(models.TextChoices):
        REGULAR = "REG", "Regular"
        CNOD = "CNOD", "CNOD"
        PARTNER = "PTN", "Partner"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    type = models.CharField(max_length=4, choices=Types.choices, default=Types.REGULAR)
    has_paid = models.BooleanField(default=False)
