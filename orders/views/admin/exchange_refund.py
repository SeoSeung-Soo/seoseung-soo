from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from config.utils.filtering import Filtering
from orders.models import Order
from orders.services.order_exchange_refund_services import OrderExchangeRefundService
from users.utils.permission import AdminPermission


class AdminExchangeRefundListView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip()

        orders_qs = Filtering.exchange_refund_list_filter(request)

        paginator = Paginator(orders_qs, 20)
        page_obj = paginator.get_page(request.GET.get("page") or "1")

        context = {
            "q": q,
            "status": status,
            "page_obj": page_obj,
            "orders": page_obj.object_list,
        }
        return render(request, "orders/admin/exchange_refund_list.html", context)


class AdminExchangeRefundProcessView(AdminPermission, View):
    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        action = request.POST.get("action")
        admin_note = request.POST.get("admin_note", "").strip()

        order = get_object_or_404(Order, id=order_id)
        
        if action == "approve":
            success, message = OrderExchangeRefundService.approve_exchange_refund(order, admin_note if admin_note else None)
        elif action == "reject":
            success, message = OrderExchangeRefundService.reject_exchange_refund(order, admin_note)
        else:
            messages.error(request, "잘못된 요청입니다.")
            return redirect("orders:admin-exchange-refund-list")
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect("orders:admin-exchange-refund-list")
