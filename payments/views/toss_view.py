import base64
import json
import os
import time
from typing import Any, Dict

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from orders.models import Order, OrderItem
from payments.models import Payment, PaymentLog
from products.models import Product
from users.models import User

TOSS_API_BASE = os.getenv("TOSS_API_BASE")


def _toss_headers() -> Dict[str, str]:
    """Toss API 공통 헤더"""
    secret_key = os.getenv("TOSS_SECRET_KEY", "")
    if not secret_key:
        raise ValueError("TOSS_SECRET_KEY not found in environment")

    encoded_key = base64.b64encode(f"{secret_key}:".encode("utf-8")).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json",
    }


# 결제 요청
@csrf_protect
def toss_payment_request_view(request: HttpRequest) -> JsonResponse:
    """Toss 결제 요청 API"""
    if request.method != "POST":
        return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

    try:
        data: Dict[str, Any] = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    order_id = data.get("orderId")
    if not order_id:
        return JsonResponse({"error": "orderId가 누락되었습니다."}, status=400)

    order = get_object_or_404(Order, order_id=order_id)

    if order.status != "PENDING":
        return JsonResponse({
            "error": f"이 주문은 이미 {order.status} 상태입니다."
        }, status=400)

    # 운영/로컬 URL 분기
    base_url = settings.HOST_URL if not settings.DEBUG else request.build_absolute_uri("/")[:-1]
    success_url = f"{base_url}/payments/toss/success/"
    fail_url = f"{base_url}/payments/toss/fail/"

    return JsonResponse({
        "success": True,
        "orderId": order.order_id,
        "amount": order.total_amount,
        "orderName": order.product_name,
        "successUrl": success_url,
        "failUrl": fail_url,
    }, status=200)


# 결제 성공
@csrf_exempt
def toss_success_view(request: HttpRequest) -> HttpResponse:
    payment_key = request.GET.get("paymentKey")
    order_id = request.GET.get("orderId")
    amount = request.GET.get("amount")
    pre_order_key = request.GET.get("preOrderKey")

    if not all([payment_key, order_id, amount]):
        return JsonResponse({"success": False, "error": "잘못된 요청입니다."}, status=400)

    confirm_url = (
        f"/payments/toss/confirm/?paymentKey={payment_key}"
        f"&orderId={order_id}&amount={amount}"
        f"&preOrderKey={pre_order_key or ''}"
    )
    return redirect(confirm_url)


# 결제 실패
@csrf_exempt
def toss_fail_view(request: HttpRequest) -> JsonResponse:
    pre_order_key = request.GET.get("preOrderKey")
    if pre_order_key:
        cache.delete(pre_order_key)  # 실패 시 즉시 캐시 제거

    return JsonResponse({
        "success": False,
        "message": request.GET.get("message", "결제 실패"),
    }, status=400)


# 결제 승인
@csrf_exempt
def toss_confirm_view(request: HttpRequest) -> JsonResponse:
    payment_key = request.GET.get("paymentKey") or ""
    order_id = request.GET.get("orderId") or ""
    amount = int(request.GET.get("amount", 0))
    pre_order_key = request.GET.get("preOrderKey") or ""

    if not all([payment_key, order_id, amount]):
        return JsonResponse({"success": False, "error": "요청 정보 누락"}, status=400)

    url = f"{TOSS_API_BASE}/payments/confirm"
    payload = {"paymentKey": payment_key, "orderId": order_id, "amount": amount}

    res = requests.post(url, headers=_toss_headers(), json=payload, timeout=10)
    data: Dict[str, Any] = res.json()

    PaymentLog.objects.create(
        provider="toss",
        event_type="CONFIRM",
        request_url=url,
        request_payload=payload,
        response_payload=data,
        status_code=res.status_code,
        response_time_ms=int((time.time() - request._start_time) * 1000) if hasattr(request, "_start_time") else 0,
    )

    if res.status_code != 200:
        return JsonResponse({"success": False, "error": data.get("message", "결제 승인 실패")}, status=400)

    if Payment.objects.filter(payment_key=payment_key).exists():
        return JsonResponse({"success": True, "message": "이미 승인된 결제입니다."}, status=200)

    # 주문 조회, 없으면 캐시로부터 생성
    order = Order.objects.filter(order_id=order_id).first()
    if not order:
        if not pre_order_key:
            return JsonResponse({"success": False, "error": "preOrderKey 누락으로 주문 생성 불가"}, status=400)
        try:
            order = create_order_from_cache(pre_order_key, order_id, data)
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    if order.total_amount != amount:
        return JsonResponse({"success": False, "error": "주문 금액이 일치하지 않습니다."}, status=400)

    with transaction.atomic():
        Payment.objects.create(
            order=order,
            provider="toss",
            method=data.get("method", "CARD"),
            payment_key=str(data.get("paymentKey") or ""),
            amount=data.get("totalAmount", amount),
            approved_at=timezone.now(),
            receipt_url=data.get("receipt", {}).get("url"),
            status="APPROVED",
            raw_response=data,
        )
        order.status = "PAID"
        order.save(update_fields=["status"])

    return JsonResponse({
        "success": True,
        "orderId": order_id,
        "paymentKey": payment_key,
        "amount": amount,
        "receipt_url": data.get("receipt", {}).get("url"),
    }, status=200)

def create_order_from_cache(pre_order_key: str, order_id: str, payment_data: Dict[str, Any]) -> Order:
    cached = cache.get(pre_order_key)
    if not cached:
        raise ValueError("주문 정보가 만료되었거나 존재하지 않습니다.")

    user = User.objects.get(id=cached["user_id"])
    items = cached["items"]
    total_amount = cached["amount"]

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            order_id=order_id,
            product_name=(
                items[0]["product_name"]
                if len(items) == 1
                else f"{items[0]['product_name']} 외 {len(items)-1}건"
            ),
            total_amount=total_amount,
            status="PENDING",
        )

        for item in items:
            product = Product.objects.get(id=item["product_id"])
            OrderItem.objects.create(
                order=order,
                product_id=product.id,
                product_name=product.name,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )

    cache.delete(pre_order_key)
    return order
