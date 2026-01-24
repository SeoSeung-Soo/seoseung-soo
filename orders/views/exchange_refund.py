from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from orders.forms.exchange_refund import OrderExchangeRefundForm
from orders.models import Order
from orders.services.order_exchange_refund_services import OrderExchangeRefundService


class OrderExchangeRefundRequestView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        return redirect("orders:status")

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        form = OrderExchangeRefundForm(request.POST)
        if form.is_valid():
            request_type = form.cleaned_data["type"]
            reason = form.cleaned_data["reason"]
            success, message = OrderExchangeRefundService.request_exchange_refund(order, request_type, reason)
        else:
            success = False
            error_messages = []
            for field_errors in form.errors.values():
                for error in field_errors:
                    error_messages.append(str(error))
            message = error_messages[0] if error_messages else "유효성 검사 실패"
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect("orders:status")
