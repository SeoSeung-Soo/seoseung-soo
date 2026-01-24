from django.db.models import Q, QuerySet
from django.http import HttpRequest

from orders.models import Order
from users.models import User


class Filtering:
    @staticmethod
    def user_list_filter(request: HttpRequest) -> QuerySet[User]:
        q = (request.GET.get("q") or "").strip()
        role = (request.GET.get("role") or "").strip()

        users_qs = User.objects.all().order_by("-date_joined")

        if q:
            users_qs = users_qs.filter(
                Q(email__icontains=q)
                | Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(phone_number__icontains=q)
            )
        if role:
            users_qs = users_qs.filter(role=role)

        return users_qs

    @staticmethod
    def order_list_filter(request: HttpRequest) -> QuerySet[Order]:
        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip()

        orders_qs = Order.objects.select_related("user").prefetch_related("items").order_by("-created_at")

        if q:
            orders_qs = orders_qs.filter(
                Q(order_id__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
                | Q(product_name__icontains=q)
            )
        if status:
            orders_qs = orders_qs.filter(status=status)
        else:
            orders_qs = orders_qs.filter(status="PAID")

        return orders_qs
    
    @staticmethod
    def cancellation_list_filter(request: HttpRequest) -> QuerySet[Order]:
        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip()

        orders_qs = Order.objects.filter(cancellation_request_status__in=["PENDING", "APPROVED", "REJECTED"]).select_related("user").prefetch_related("items").order_by("-cancellation_requested_at")

        if q:
            orders_qs = orders_qs.filter(
                Q(order_id__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
                | Q(product_name__icontains=q)
            )
        if status:
            orders_qs = orders_qs.filter(cancellation_request_status=status)

        return orders_qs
    
    @staticmethod
    def exchange_refund_list_filter(request: HttpRequest) -> QuerySet[Order]:
        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip()

        orders_qs = Order.objects.filter(exchange_refund_request_status__in=["PENDING", "APPROVED", "REJECTED"]).select_related("user").prefetch_related("items").order_by("-exchange_refund_requested_at")

        if q:
            orders_qs = orders_qs.filter(
                Q(order_id__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
                | Q(product_name__icontains=q)
            )
        if status:
            orders_qs = orders_qs.filter(exchange_refund_request_status=status)

        return orders_qs