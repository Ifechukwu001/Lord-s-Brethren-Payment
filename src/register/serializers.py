from rest_framework import serializers
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DJRegisterSerializer,
)

from .models import Participant


class RegisterSerializer(DJRegisterSerializer, serializers.ModelSerializer):
    username = None
    password1 = None
    password2 = None
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Participant
        fields = [
            "firstname",
            "lastname",
            "email",
            "password",
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
        ]

    def get_email(self, instance):
        return instance.user.email

    def validate_email(self, email):
        email = super().validate_email(email)
        if Participant.objects.filter(user__email=email).exists():
            raise serializers.ValidationError(
                "Partricipant with this email already exists"
            )
        return email

    def validate_password(self, value):
        return super().validate_password1(value)

    def validate(self, data):
        data["password1"] = data["password"]
        return data

    def save(self, request):
        user = super().save(request)
        self.remove_fields(["email", "password1", "password"])
        Participant.objects.create(user=user, **self.validated_data)
        return user

    def remove_fields(self, fields):
        for field in fields:
            self.validated_data.pop(field)


class ParticipantSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
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
