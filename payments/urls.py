from django.urls import path

from payments.views.toss_view import (
    toss_confirm_view,
    toss_fail_view,
    toss_payment_request_view,
    toss_success_view,
)

app_name = "payments"

urlpatterns = [
    path("toss/request/", toss_payment_request_view, name="toss-request"),
    path("toss/success/", toss_success_view, name="toss-success"),
    path("toss/fail/", toss_fail_view, name="toss-fail"),
    path("toss/confirm/", toss_confirm_view, name="toss-confirm"),
]
