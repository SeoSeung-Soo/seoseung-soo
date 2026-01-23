from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from orders.models import Order
from products.models import Product
from users.models import User


class OrderView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)

        orders = Order.objects.filter(user=user)
        order_stats = {
            'pending': orders.filter(status='PENDING').count(),
            'preparing': orders.filter(status='PAID', shipping_status='PENDING').count(),
            'shipping': orders.filter(status='PAID', shipping_status='SHIPPING').count(),
            'delivered': orders.filter(status='PAID', shipping_status='DELIVERED').count(),
        }

        cart_stats = {
            'items': orders.filter(status='CANCELLED').count(),
            'likes': 0,
            'reviews': 0,
        }

        recent_orders = orders.order_by('-created_at').prefetch_related(
            'items__color'
        )[:10]

        all_product_ids = []
        for order in recent_orders:
            order.items_list = list(order.items.all())  # type: ignore[attr-defined]
            for item in order.items_list:  # type: ignore[attr-defined]
                if item.product_id not in all_product_ids:
                    all_product_ids.append(item.product_id)

        if all_product_ids:
            products = Product.objects.filter(id__in=all_product_ids).prefetch_related('image', 'colors')
            products_dict = {p.id: p for p in products}
        else:
            products_dict = {}

        for order in recent_orders:
            for item in order.items_list:  # type: ignore[attr-defined]
                item.product = products_dict.get(item.product_id)

        payment_success = request.session.pop('payment_success', False)
        order_id = request.session.pop('order_id', None)

        context = {
            'user': user,
            'order_stats': order_stats,
            'cart_stats': cart_stats,
            'recent_orders': recent_orders,
            'current_page': 'orders',
            'payment_success': payment_success,
            'order_id': order_id,
        }

        return render(request, "orders/order_mypage.html", context)


