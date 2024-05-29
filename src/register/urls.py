from django.urls import path

from .views import RegisterView, ParticipantAPIView, GenerateTicketPaymentAPIView

app_name = "register"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("participant/", ParticipantAPIView.as_view(), name="participant"),
    path(
        "ticket-payment/",
        GenerateTicketPaymentAPIView.as_view(),
        name="generate-ticket-payment",
    ),
]
