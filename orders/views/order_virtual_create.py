import json
from typing import Any, Dict, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from orders.models import Order, OrderItem
from orders.services.order_services import OrderService
from payments.services.toss_payment_service import TossPaymentService
from users.models import User


@method_decorator(csrf_protect, name="dispatch")
class OrderCreateVirtualView(LoginRequiredMixin, View):
    """
    무통장입금용 주문 생성
    실제 Order + OrderItem을 DB에 바로 생성
    """
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data: Dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

        items_data = data.get("items", [])

        is_valid, error_message, validated_items, total_amount = (
            OrderService.validate_and_prepare_order_items(items_data)
        )

        if not is_valid:
            return JsonResponse({"error": error_message}, status=400)

        user = cast(User, request.user)
        order_id = TossPaymentService.generate_order_id()
        order_name = TossPaymentService.generate_order_name(validated_items)

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                order_id=order_id,
                product_name=order_name,
                total_amount=float(total_amount),
                status="PENDING",
                created_at=timezone.now()
            )

            for item in validated_items:
                OrderItem.objects.create(
                    order=order,
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )

        return JsonResponse({
            "success": True,
            "orderId": order_id,
            "totalAmount": int(total_amount),
            "status": "PENDING",
        }, status=200)
