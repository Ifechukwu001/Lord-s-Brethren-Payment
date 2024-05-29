from django.urls import path

from .views import RegisterView, GenerateTicketPaymentAPIView

app_name = "register"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "ticket-payment/",
        GenerateTicketPaymentAPIView.as_view(),
        name="generate-ticket-payment",
    ),
]
