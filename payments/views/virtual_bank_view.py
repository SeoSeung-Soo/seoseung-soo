import json
import re
from typing import Any, Dict

import requests
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from orders.models import Order
from payments.models import BankChoices, Payment
from payments.services.toss_payment_service import TossPaymentService

TOSS_API_BASE = settings.TOSS_API_BASE


@method_decorator(csrf_protect, name="dispatch")
class TossVirtualRequestView(View):
    """무통장입금(가상계좌) 결제 요청 (기존 주문 기반)"""

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data: Dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

        order_id = data.get("orderId")
        customer_name = data.get("customerName")
        bank = data.get("bank")

        valid_banks = [choice[0] for choice in BankChoices.choices]
        if bank not in valid_banks:
            return JsonResponse({
                "error": f"유효하지 않은 은행 코드입니다. 허용된 코드: {valid_banks}"
            }, status=400)

        if not all([order_id, customer_name, bank]):
            return JsonResponse({"error": "필수 정보 누락"}, status=400)

        order = get_object_or_404(Order, order_id=order_id)

        base_url = settings.HOST_URL if not settings.DEBUG else request.build_absolute_uri("/")[:-1]
        success_url = f"{base_url}/payments/toss/success/"
        fail_url = f"{base_url}/payments/toss/fail/"

        payload = {
            "method": "VIRTUAL_ACCOUNT",
            "amount": order.total_amount,
            "orderId": order.order_id,
            "orderName": order.product_name,
            "customerName": customer_name,
            "bank": bank,
            "validHours": 24,
            "successUrl": success_url,
            "failUrl": fail_url,
        }

        res = requests.post(
            f"{TOSS_API_BASE}/virtual-accounts",
            headers=TossPaymentService.get_toss_headers(),
            json=payload,
            timeout=10,
        )

        try:
            data = res.json()
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": f"Toss 응답이 JSON 형식이 아닙니다: {res.text[:200]}"
            }, status=500)

        if res.status_code != 200:
            return JsonResponse({
                "success": False,
                "error": data.get("message", "결제 요청 실패"),
                "status_code": res.status_code,
                "response": data,
            }, status=400)

        va = data.get("virtualAccount")
        if not va:
            return JsonResponse({
                "success": False,
                "error": "Toss 응답에 가상계좌 정보가 포함되지 않았습니다.",
                "response": data,
            }, status=400)

        payment_key = str(data.get("paymentKey") or "")

        # 계좌번호 정규화
        account_number_raw = va.get("accountNumber", "")
        account_number = re.sub(r"[^0-9]", "", account_number_raw)

        with transaction.atomic():
            Payment.objects.create(
                order=order,
                provider="toss",
                method="VIRTUAL_ACCOUNT",
                payment_key=payment_key,
                amount=order.total_amount,
                bank_name=va.get("bank"),
                account_number=account_number,
                account_holder=va.get("customerName"),
                due_date=va.get("dueDate"),
                status="WAITING_FOR_DEPOSIT",
                raw_response=data,
            )

        return JsonResponse({
            "success": True,
            "orderId": order.order_id,
            "bank": va.get("bank"),
            "account_number": va.get("accountNumber"),
            "account_holder": va.get("customerName"),
            "due_date": va.get("dueDate"),
        }, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class TossVirtualWebhookView(View):
    """토스 가상계좌 입금 웹훅"""

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식"}, status=400)

        payment_key = data.get("paymentKey")
        order_id = data.get("orderId")
        status = data.get("status")

        if not (payment_key and order_id):
            return JsonResponse({"error": "필수 필드 누락"}, status=400)

        payment = Payment.objects.filter(payment_key=payment_key).select_related("order").first()
        if not payment:
            return JsonResponse({"error": "유효하지 않은 paymentKey입니다."}, status=404)

        if status == "DONE":
            with transaction.atomic():
                payment.raw_response = data
                payment.save(update_fields=["raw_response"])
                payment.approve()

            return JsonResponse({"success": True, "message": "입금 완료 처리됨"})

        return JsonResponse({"success": True, "message": f"상태: {status}"})