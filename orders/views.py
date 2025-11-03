import json
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from products.models import Product

from .models import Order, OrderItem


def generate_order_id() -> str:
    now = timezone.now().strftime("%Y%m%d%H%M%S")
    rand = uuid.uuid4().hex[:6].upper()
    return str(f"ORD-{now}-{rand}")


# 주문명 생성기
def _build_order_name(items: List[Dict[str, Any]]) -> str:
    if len(items) == 1:
        return str(items[0].get("product_name", "상품"))
    return f"{items[0].get('product_name', '상품')} 외 {len(items) - 1}건"


# 주문 생성
@csrf_protect
def create_order_view(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

    try:
        data: Dict[str, Any] = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    items_data: List[Dict[str, Any]] = data.get("items", [])
    if not items_data:
        return JsonResponse({"error": "주문 항목이 비어있습니다."}, status=400)

    # 실제 DB 기준으로 금액 계산
    total_amount: Decimal = Decimal("0.0")
    order_items: List[Tuple[Product, int, Decimal]] = []

    for item in items_data:
        product = get_object_or_404(Product, id=item["product_id"])
        price = Decimal(product.sale_price or product.price)
        quantity = int(item.get("quantity", 1))
        total_amount += price * quantity
        order_items.append((product, quantity, price))

    order_id = generate_order_id()

    order = Order.objects.create(
        user=request.user,
        order_id=order_id,
        product_name=_build_order_name(items_data),
        total_amount=int(total_amount),
        status="PENDING",
    )

    for product, quantity, price in order_items:
        OrderItem.objects.create(
            order=order,
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=int(price)
        )

    return JsonResponse({
        "success": True,
        "orderId": order.order_id,
        "orderName": order.product_name,
        "amount": total_amount,
    }, status=201)
