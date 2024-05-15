from rest_framework import serializers
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DJRegisterSerializer,
)

from .models import Participant


class RegisterSerializer(DJRegisterSerializer, serializers.ModelSerializer):
    username = None
    password1 = None
    password2 = None
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Participant
        fields = [
            "email",
            "password",
            "name",
            "phone",
            "category",
        ]

    def validate_email(self, value):
        email = super().validate_email(value)
        if Participant.objects.filter(user__email=email).exists():
            raise serializers.ValidationError("Email already exists")
        return email

    def validate_password(self, value):
        return super().validate_password1(value)

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email"),
            "password1": self.validated_data.get("password1"),
            "name": self.validated_data.get("name"),
            "phone": self.validated_data.get("phone"),
            "category": self.validated_data.get("category"),
        }

    def validate(self, data):
        data["password1"] = data["password"]
        return data

    def save(self, request):
        user = super().save(request)
        Participant.objects.create(
            user=user,
            name=self.validated_data.get("name"),
            phone=self.validated_data.get("phone"),
            category=self.validated_data.get("category"),
        )
        return user
