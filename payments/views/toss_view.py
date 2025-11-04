import base64
import json
import time
from typing import Any, Dict

import requests
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from orders.models import Order
from payments.models import Payment, PaymentLog


def _toss_headers() -> Dict[str, str]:
    """Toss API 공통 헤더"""
    secret_key = getattr(settings, 'TOSS_SECRET_KEY', '')
    if not secret_key:
        raise ValueError("TOSS_SECRET_KEY not found in settings")

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

    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

    try:
        data: Dict[str, Any] = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    order_id = data.get("orderId")
    if not order_id:
        return JsonResponse({"error": "orderId가 누락되었습니다."}, status=400)

    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status != "PENDING":
        return JsonResponse({
            "error": f"이 주문은 이미 {order.status} 상태입니다."
        }, status=400)

    # 배송비 계산 (5만원 이상 무료, 미만 3000원)
    shipping_fee = 0 if order.total_amount >= 50000 else 3000
    final_amount = order.total_amount + shipping_fee

    # 운영/로컬 URL 분기
    base_url = settings.HOST_URL if not settings.DEBUG else request.build_absolute_uri("/")[:-1]
    success_url = f"{base_url}/payments/toss/success/"
    fail_url = f"{base_url}/payments/toss/fail/"

    return JsonResponse({
        "success": True,
        "orderId": order.order_id,
        "amount": final_amount,  # 배송비 포함 최종 금액
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

    if not all([payment_key, order_id, amount]):
        return JsonResponse({"success": False, "error": "잘못된 요청입니다."}, status=400)

    confirm_url = f"/payments/toss/confirm/?paymentKey={payment_key}&orderId={order_id}&amount={amount}"
    return redirect(confirm_url)


# 결제 실패
@csrf_exempt
def toss_fail_view(request: HttpRequest) -> JsonResponse:
    code = request.GET.get("code")
    message = request.GET.get("message")
    return JsonResponse({
        "success": False,
        "error_code": code,
        "message": message
    })


# 결제 승인
@csrf_exempt
def toss_confirm_view(request: HttpRequest) -> JsonResponse:
    payment_key = request.GET.get("paymentKey")
    order_id = request.GET.get("orderId")
    amount = int(request.GET.get("amount", 0))

    if not all([payment_key, order_id, amount]):
        return JsonResponse({"success": False, "error": "요청 정보 누락"}, status=400)

    toss_api_base = getattr(settings, 'TOSS_API_BASE', 'https://api.tosspayments.com/v1')
    url = f"{toss_api_base}/payments/confirm"
    payload = {
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": amount,
    }

    start = time.time()
    try:
        res = requests.post(url, headers=_toss_headers(), json=payload, timeout=10)
        elapsed = int((time.time() - start) * 1000)
        data: Dict[str, Any] = res.json()

        PaymentLog.objects.create(
            provider="toss",
            event_type="CONFIRM",
            request_url=url,
            request_payload=payload,
            response_payload=data,
            status_code=res.status_code,
            response_time_ms=elapsed,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": f"결제 승인 요청 중 오류 발생: {str(e)}"}, status=500)

    if res.status_code != 200:
        return JsonResponse({"success": False, "error": data.get("message", "결제 승인 실패")}, status=400)

    order = get_object_or_404(Order, order_id=order_id)

    # 배송비 포함 금액 검증
    shipping_fee = 0 if order.total_amount >= 50000 else 3000
    expected_amount = order.total_amount + shipping_fee

    if expected_amount != amount:
        return JsonResponse({
            "success": False, 
            "error": f"주문 금액이 일치하지 않습니다. 예상: {expected_amount}, 실제: {amount}"
        }, status=400)

    with transaction.atomic():
        Payment.objects.create(
            order=order,
            provider="toss",
            method=data.get("method", "CARD"),
            payment_key=data.get("paymentKey", ""),
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
    })