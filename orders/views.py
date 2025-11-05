import json
import uuid
from decimal import Decimal
from typing import Any, Dict, List

from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from products.models import Product


def generate_preorder_key() -> str:
    """결제 전 임시 주문 캐시 키 생성"""
    return f"preorder:{uuid.uuid4().hex[:10]}"


@csrf_protect
def create_order_view(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

    # JSON 파싱
    try:
        data: Dict[str, Any] = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    items_data: List[Dict[str, Any]] = data.get("items", [])
    if not items_data:
        return JsonResponse({"error": "주문 항목이 비어있습니다."}, status=400)

    product_ids = [item["product_id"] for item in items_data if "product_id" in item]
    products = Product.objects.filter(id__in=product_ids)
    product_map = {p.id: p for p in products}

    # 존재하지 않는 상품 확인
    if len(product_ids) != len(product_map):
        return JsonResponse({"error": "존재하지 않는 상품이 포함되어 있습니다."}, status=404)

    total_amount = Decimal("0.0")
    validated_items: List[Dict[str, Any]] = []

    for item in items_data:
        product_id = item["product_id"]
        product = product_map[product_id]

        quantity = int(item.get("quantity", 1))
        price = Decimal(product.sale_price or product.price)

        total_amount += price * quantity

        validated_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": quantity,
            "unit_price": int(price),
        })

    preorder_key = generate_preorder_key()
    cache_data = {
        "user_id": request.user.id,
        "items": validated_items,
        "amount": int(total_amount),
        "created_at": timezone.now().isoformat(),
    }

    # Redis / Django Cache에 15분간 저장
    cache.set(preorder_key, cache_data, timeout=60 * 15)

    return JsonResponse({
        "success": True,
        "preOrderKey": preorder_key,
        "amount": int(total_amount),
        "items": validated_items,
        "expires_in": "15분",
    }, status=200)