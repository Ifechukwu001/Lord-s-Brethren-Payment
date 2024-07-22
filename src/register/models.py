from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
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
    reference = models.CharField(max_length=20, editable=False, unique=True, null=True)
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

            self.transaction = Transaction.objects.create(
                email=self.email, amount=amount, currency="NGN"
            )
            self.save()

        return self.transaction.generate_payment_link(description, callback_url)

    @property
    def has_paid(self) -> bool:
        result = False
        if self.transaction:
            result = self.transaction.is_success
        return result


@receiver(post_save, sender=Participant)
def generate_participant_ref(sender, instance, created, **kwargs):
    if not instance.reference:
        instance.reference = f"TLBC24{instance.id:004}"
    if created:
        instance.save()


class Partner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True)
    reference = models.CharField(max_length=20, editable=False, unique=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return {self.name}

    def generate_payment_link(self, amount=None, currency=None, callback_url=None):
        description = "Partner Payment for Conference"
        if not self.transaction:
            if not amount or not currency:
                raise ValueError("Amount and Currency are required")

            self.transaction = Transaction.objects.create(
                email=self.email, amount=amount, currency=currency
            )
            self.save()

        return self.transaction.generate_payment_link(description, callback_url)

    @property
    def has_paid(self) -> bool:
        result = False
        if self.transaction:
            result = self.transaction.is_success
        return result


@receiver(post_save, sender=Partner)
def generate_partner_ref(sender, instance, created, **kwargs):
    if not instance.reference:
        instance.reference = f"TLBC24{instance.id:004}P"
    if created:
        instance.save()
