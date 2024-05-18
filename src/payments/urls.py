from django.urls import path

from .views import TransactionCreateView

urlpatterns = [
    path("payment/", TransactionCreateView.as_view(), name="start_transaction"),
]
