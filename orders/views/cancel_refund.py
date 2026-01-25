from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from orders.models import Order
from products.models import Product
from users.models import User


class CancelRefundView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)

        orders = Order.objects.filter(user=user)

        order_stats = {
            'preparing': orders.filter(status=Order.Status.PAID, shipping_status=Order.ShippingStatus.PENDING).count(),
            'shipping': orders.filter(status=Order.Status.PAID, shipping_status=Order.ShippingStatus.SHIPPING).count(),
            'delivered': orders.filter(status=Order.Status.PAID, shipping_status=Order.ShippingStatus.DELIVERED).count(),
        }

        cancellation_exchange_refund_stats = {
            'cancellation': orders.filter(
                cancellation_request_status__in=[Order.CancellationRequestStatus.PENDING, Order.CancellationRequestStatus.APPROVED]
            ).count(),
            'exchange': orders.filter(
                exchange_refund_request_status__in=[Order.ExchangeRefundRequestStatus.PENDING, Order.ExchangeRefundRequestStatus.APPROVED],
                exchange_refund_type=Order.ExchangeRefundType.EXCHANGE
            ).count(),
            'refund': orders.filter(
                exchange_refund_request_status__in=[Order.ExchangeRefundRequestStatus.PENDING, Order.ExchangeRefundRequestStatus.APPROVED],
                exchange_refund_type=Order.ExchangeRefundType.REFUND
            ).count(),
        }

        cancellation_exchange_refund_orders = orders.filter(
            cancellation_request_status__in=[Order.CancellationRequestStatus.PENDING, Order.CancellationRequestStatus.APPROVED, Order.CancellationRequestStatus.REJECTED]
        ) | orders.filter(
            exchange_refund_request_status__in=[Order.ExchangeRefundRequestStatus.PENDING, Order.ExchangeRefundRequestStatus.APPROVED, Order.ExchangeRefundRequestStatus.REJECTED]
        )
        cancellation_exchange_refund_orders = cancellation_exchange_refund_orders.distinct().order_by('-created_at').prefetch_related('items__color')[:10]

        all_product_ids = []
        for order in cancellation_exchange_refund_orders:
            order.items_list = list(order.items.all())  # type: ignore[attr-defined]
            for item in order.items_list:  # type: ignore[attr-defined]
                if item.product_id not in all_product_ids:
                    all_product_ids.append(item.product_id)

        if all_product_ids:
            products = Product.objects.filter(id__in=all_product_ids).prefetch_related('image', 'colors')
            products_dict = {p.id: p for p in products}
        else:
            products_dict = {}

        for order in cancellation_exchange_refund_orders:
            for item in order.items_list:  # type: ignore[attr-defined]
                item.product = products_dict.get(item.product_id)

        context = {
            'user': user,
            'order_stats': order_stats,
            'cancellation_exchange_refund_stats': cancellation_exchange_refund_stats,
            'cancellation_exchange_refund_orders': cancellation_exchange_refund_orders,
            'current_page': 'orders',
        }

        return render(request, "orders/cancel_refund.html", context)
