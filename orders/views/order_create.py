import json
from typing import Any, Dict, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from orders.services.order_services import OrderService
from users.models import User


@method_decorator(csrf_protect, name='dispatch')
class OrderCreateView(LoginRequiredMixin, View):
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
        preorder_key = OrderService.create_preorder_cache(
            user_id=user.id,
            validated_items=validated_items,
            total_amount=total_amount,
        )

        return JsonResponse({
            "success": True,
            "preOrderKey": preorder_key,
            "amount": int(total_amount),
            "items": validated_items,
            "expires_in": "15분",
        }, status=200)