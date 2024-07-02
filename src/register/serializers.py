from rest_framework import serializers

from .models import Participant


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
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

    def save(self):
        if "callback_url" in self.validated_data:
            self.validated_data.pop("callback_url")
        return super().save()


class ParticipantSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
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


class GenerateTicketSerializer(serializers.Serializer):
    callback_url = serializers.URLField(required=False)
