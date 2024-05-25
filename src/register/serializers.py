from rest_framework import serializers
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DJRegisterSerializer,
)

from .models import Participant


class RegisterSerializer(serializers.ModelSerializer):
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
        ]

    def save(self):
        participant = Participant.objects.create(**self.validated_data)
        return participant
