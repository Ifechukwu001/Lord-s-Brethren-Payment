from django.db import models

from core.env import config
from payments.models import Transaction


class Participant(models.Model):
    class Types(models.TextChoices):
        INVITEE = "Invitee"
        MEMBER = "Member"

    class Gender(models.TextChoices):
        MALE = "M"
        FEMALE = "F"

    class Attendance(models.TextChoices):
        CAMPER = "Camper"
        DAILY = "Daily"
        STREAMER = "Streamer"

    class Reach(models.TextChoices):
        FACEBOOK = "Facebook"
        WHATSAPP = "WhatsApp"
        INSTAGRAM = "Instagram"
        CHURCH = "Church"
        WEBSITE = "Website"
        OUTREACH = "Outreach"
        FRIEND = "Friend"

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=2, choices=Gender.choices, default=Gender.MALE)
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    category = models.CharField(
        max_length=10, choices=Types.choices, default=Types.INVITEE
    )
    church_name = models.CharField(max_length=100)
    attendance_mode = models.CharField(
        max_length=10, choices=Attendance.choices, default=Attendance.CAMPER
    )
    was_participant = models.BooleanField(default=False)
    is_aware_of_convention = models.BooleanField(default=False)
    health_issue = models.TextField(null=True, blank=True)
    reach = models.CharField(max_length=10, choices=Reach.choices, default=Reach.CHURCH)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def generate_payment_link(self, callback_url=None):
        description = "Ticket Payment for Conference"
        if not self.transaction:
            if self.category == self.Types.MEMBER:
                amount = config("MEMBER_PRICE")
            else:
                amount = config("INVITEE_PRICE")

            reference = f"TLBC24{self.id:004}"
            self.transaction = Transaction.objects.create(
                email=self.email, amount=amount, currency="NGN", reference=reference
            )
            self.save()

        return self.transaction.generate_payment_link(description, callback_url)

    @property
    def has_paid(self) -> bool:
        result = False
        if self.transaction:
            result = self.transaction.is_success
        return result
