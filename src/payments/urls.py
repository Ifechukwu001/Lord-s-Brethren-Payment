from django.urls import path

from .views import TransactionCreateView, TransactionWebHook, TransactionVerifyAPIView

urlpatterns = [
    path("payment/", TransactionCreateView.as_view(), name="start_transaction"),
    path(
        "payment/verify/", TransactionVerifyAPIView.as_view(), name="verify_transaction"
    ),
    path("payment-hook/", TransactionWebHook.as_view(), name="webhook"),
]
