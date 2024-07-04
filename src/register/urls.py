from django.urls import path

from .views import (
    ParticipantRegisterView,
    PartnerRegisterView,
    ParticipantAPIView,
    PartnerAPIView,
    SearchAPIView,
    GeneratePaymentLinkAPIView,
)

app_name = "register"

urlpatterns = [
    path("register/", ParticipantRegisterView.as_view(), name="register"),
    path(
        "participant/<str:reference>/", ParticipantAPIView.as_view(), name="participant"
    ),
    path("partner/", PartnerRegisterView.as_view(), name="partner_register"),
    path("partner/<str:reference>/", PartnerAPIView.as_view(), name="partner"),
    path("search/<str:email>/", SearchAPIView.as_view(), name="search"),
    path(
        "generate-payment-link/",
        GeneratePaymentLinkAPIView.as_view(),
        name="generate-payment-link",
    ),
]
