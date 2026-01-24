from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from orders.models import Order
from orders.services.order_cancellation_services import OrderCancellationService


class OrderCancellationRequestView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        return redirect("orders:status")

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        reason = request.POST.get("reason", "").strip()
        
        success, message = OrderCancellationService.request_cancellation(order, reason)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect("orders:status")
