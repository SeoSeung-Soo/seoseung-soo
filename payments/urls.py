from django.urls import path

from payments.views import (
    PaymentView,
    TossConfirmView,
    TossFailView,
    TossPaymentRequestView,
    TossSuccessView,
)

app_name = "payments"

urlpatterns = [
    path("", PaymentView.as_view(), name="payment"),
    path("toss/request/", TossPaymentRequestView.as_view(), name="toss-request"),
    path("toss/success/", TossSuccessView.as_view(), name="toss-success"),
    path("toss/fail/", TossFailView.as_view(), name="toss-fail"),
    path("toss/confirm/", TossConfirmView.as_view(), name="toss-confirm"),
]
