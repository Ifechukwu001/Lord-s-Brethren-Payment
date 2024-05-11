from django.contrib import admin
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "phone", "type", "has_paid"]
    search_fields = ["name", "phone"]
    list_filter = ["type", "has_paid"]
