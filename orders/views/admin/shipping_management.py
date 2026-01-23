from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from orders.models import Order
from users.utils.permission import AdminPermission


class ShippingManagementView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        q = (request.GET.get("q") or "").strip()
        shipping_status = (request.GET.get("shipping_status") or "").strip()

        orders_qs: QuerySet[Order] = Order.objects.filter(status="PAID").select_related("user").prefetch_related("items").order_by("-created_at")

        if q:
            orders_qs = orders_qs.filter(
                Q(order_id__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
                | Q(product_name__icontains=q)
            )

        if shipping_status:
            orders_qs = orders_qs.filter(shipping_status=shipping_status)

        paginator = Paginator(orders_qs, 20)
        page_obj = paginator.get_page(request.GET.get("page") or "1")

        context = {
            "q": q,
            "shipping_status": shipping_status,
            "page_obj": page_obj,
            "orders": page_obj.object_list,
        }
        return render(request, "orders/admin/shipping_management.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("shipping_status")

        if not order_id or not new_status:
            messages.error(request, "주문 ID와 배송 상태를 모두 입력해주세요.")
            return redirect("orders:admin-shipping-management")

        order = get_object_or_404(Order, id=order_id, status="PAID")
        
        old_status = order.get_shipping_status_display()
        order.shipping_status = new_status
        order.save()

        new_status_display = order.get_shipping_status_display()
        messages.success(request, f"주문 {order.order_id}의 배송 상태가 '{old_status}'에서 '{new_status_display}'로 변경되었습니다.")

        redirect_url = reverse("orders:admin-shipping-management")
        return redirect(f"{redirect_url}?shipping_status={new_status}")
