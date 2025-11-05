import base64
import json
import os
from typing import Any, Dict

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from orders.models import Order
from payments.models import Payment, PaymentLog

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
    payment_key = request.GET.get("paymentKey")
    order_id = request.GET.get("orderId")
    amount = int(request.GET.get("amount", 0))
    pre_order_key = request.GET.get("preOrderKey")

    if not all([payment_key, order_id, amount]):
        return JsonResponse({"success": False, "error": "요청 정보 누락"}, status=400)

    url = f"{TOSS_API_BASE}/payments/confirm"
    payload = {"paymentKey": payment_key, "orderId": order_id, "amount": amount}

    try:
        res = requests.post(url, headers=_toss_headers(), json=payload, timeout=10)
        data: Dict[str, Any] = res.json()
    except requests.exceptions.RequestException as e:
        PaymentLog.objects.create(
            provider="toss",
            event_type="CONFIRM",
            request_url=url,
            request_payload=payload,
            response_payload={"error": str(e)},
            status_code=503,
        )
        return JsonResponse({"success": False, "error": "결제 승인 요청 중 오류 발생"}, status=500)

    if res.status_code != 200:
        PaymentLog.objects.create(
            provider="toss",
            event_type="CONFIRM_FAIL",
            request_url=url,
            request_payload=payload,
            response_payload=data,
            status_code=res.status_code,
        )
        return JsonResponse(
            {"success": False, "error": data.get("message", "결제 승인 실패")},
            status=400,
        )

    if not pre_order_key:
        return JsonResponse({"success": False, "error": "preOrderKey 누락"}, status=400)

    cache_data = cache.get(pre_order_key)
    if cache_data is None:
        return JsonResponse(
            {"success": False, "error": "preOrderKey가 만료되었거나 유효하지 않습니다."},
            status=400,
        )

    user = get_user_model().objects.filter(id=cache_data["user_id"]).first()
    if not user:
        return JsonResponse({"success": False, "error": "유효하지 않은 사용자"}, status=400)

    expected_amount = int(cache_data.get("amount", 0))
    if expected_amount != amount:
        return JsonResponse(
            {"success": False, "error": "결제 금액이 주문 정보와 일치하지 않습니다."}, status=400
        )

    if Payment.objects.filter(payment_key=payment_key).exists():
        return JsonResponse({"success": True, "message": "이미 승인된 결제입니다."}, status=200)

    order, created = Order.objects.get_or_create(
        order_id=order_id,
        defaults={
            "user": user,
            "total_amount": amount,
            "status": "PENDING",
        },
    )

    with transaction.atomic():
        Payment.objects.create(
            order=order,
            provider="toss",
            method=data.get("method", "CARD"),
            payment_key=str(payment_key),
            amount=amount,
            receipt_url=data.get("receipt", {}).get("url", ""),
            status="APPROVED",
            raw_response=data,
        )
        order.status = "PAID"
        order.save(update_fields=["status"])

        PaymentLog.objects.create(
            provider="toss",
            event_type="CONFIRM",
            request_url=url,
            request_payload=payload,
            response_payload=data,
            status_code=res.status_code,
        )

        cache.delete(pre_order_key)

    return JsonResponse(
        {
            "success": True,
            "orderId": order_id,
            "paymentKey": payment_key,
            "amount": amount,
            "receipt_url": data.get("receipt", {}).get("url"),
        },
        status=200,
    )
