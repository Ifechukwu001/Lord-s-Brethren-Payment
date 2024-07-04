from django.urls import path

from .views import (
    ParticipantRegisterView,
    PartnerRegisterView,
    ParticipantAPIView,
    PartnerAPIView,
    GenerateTicketPaymentAPIView,
)

app_name = "register"

urlpatterns = [
    path("register/", ParticipantRegisterView.as_view(), name="register"),
    path(
        "participant/<str:reference>/", ParticipantAPIView.as_view(), name="participant"
    ),
    path("partner/", PartnerRegisterView.as_view(), name="partner_register"),
    path("partner/<str:reference>/", PartnerAPIView.as_view(), name="partner"),
    # path(
    #     "ticket-payment/",
    #     GenerateTicketPaymentAPIView.as_view(),
    #     name="generate-ticket-payment",
    # ),
]
