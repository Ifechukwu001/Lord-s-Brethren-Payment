from decimal import Decimal
from rest_framework import serializers
import moneyed

from .models import Participant, Partner


class ParticipantRegisterSerializer(serializers.ModelSerializer):
    callback_url = serializers.URLField(required=False)

    class Meta:
        model = Participant
        fields = [
            "firstname",
            "lastname",
            "email",
            "phone",
            "gender",
            "birthdate",
            "address",
            "category",
            "church_name",
            "attendance_mode",
            "was_participant",
            "is_aware_of_convention",
            "health_issue",
            "reach",
            "callback_url",
        ]

    def validate_email(self, value):
        if Participant.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Participant with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Participant.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Participant with this phone already exists."
            )
        return value

    def save(self):
        if "callback_url" in self.validated_data:
            self.validated_data.pop("callback_url")
        return super().save()


class PartnerRegisterSerializer(serializers.ModelSerializer):
    callback_url = serializers.URLField(required=False)
    currency = serializers.ChoiceField(
        choices=[
            (currency.code, currency.name) for currency in moneyed.list_all_currencies()
        ],
        default="NGN",
    )
    amount = serializers.DecimalField(
        min_value=Decimal(0.00), max_digits=10, decimal_places=2
    )

    class Meta:
        model = Partner
        fields = [
            "name",
            "email",
            "phone",
            "country",
            "state",
            "currency",
            "amount",
            "callback_url",
        ]

    def save(self):
        if "callback_url" in self.validated_data:
            self.validated_data.pop("callback_url")
        if "currency" in self.validated_data:
            self.validated_data.pop("currency")
        if "amount" in self.validated_data:
            self.validated_data.pop("amount")
        return super().save()


class ParticipantSerializer(serializers.ModelSerializer):
    category = serializers.CharField(read_only=True)

    class Meta:
        model = Participant
        fields = [
            "firstname",
            "lastname",
            "email",
            "phone",
            "gender",
            "birthdate",
            "address",
            "category",
            "church_name",
            "attendance_mode",
            "was_participant",
            "is_aware_of_convention",
            "health_issue",
            "reach",
            "has_paid",
        ]


class ParticipantWithRefSerializer(ParticipantSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source="transaction.amount",
        read_only=True,
        coerce_to_string=False,
    )
    currency = serializers.CharField(source="transaction.currency", read_only=True)

    class Meta(ParticipantSerializer.Meta):
        fields = ParticipantSerializer.Meta.fields + ["reference", "amount", "currency"]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = [
            "name",
            "email",
            "phone",
            "country",
            "state",
            "has_paid",
        ]


class PartnerWithRefSerializer(PartnerSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source="transaction.amount",
        read_only=True,
        coerce_to_string=False,
    )
    currency = serializers.CharField(source="transaction.currency", read_only=True)

    class Meta(PartnerSerializer.Meta):
        fields = PartnerSerializer.Meta.fields + ["reference", "amount", "currency"]


class SearchSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    firstname = serializers.CharField(required=False)
    lastname = serializers.CharField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("firstname") and data.get("lastname"):
            data["name"] = f"{data.pop('firstname')} {data.pop('lastname')}"
        else:
            data.pop("firstname", None)
            data.pop("lastname", None)
        return data


class GenerateSerializer(serializers.Serializer):
    callback_url = serializers.URLField(required=False)
    reference = serializers.CharField()
