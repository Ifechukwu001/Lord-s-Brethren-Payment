from django.conf import settings
from django.db import models


class Participant(models.Model):
    class Types(models.TextChoices):
        INVITEE = "Invitee"
        MEMBER = "Member"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    category = models.CharField(
        max_length=10, choices=Types.choices, default=Types.INVITEE
    )
    has_paid = models.BooleanField(default=False)
