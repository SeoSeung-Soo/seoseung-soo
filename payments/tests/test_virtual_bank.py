import json
from typing import Any
from unittest.mock import patch

import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order
from payments.models import Payment


@pytest.mark.django_db(transaction=True)
class TestTossVirtualAccountFlow(TestSetupMixin):
    """Toss 가상계좌 발급 및 입금완료 웹훅 테스트"""
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

        self.order = Order.objects.create(
            user=self.customer_user,
            order_id="ORD-TEST-12345",
            product_name=self.product.name,
            total_amount=float(self.product.price),
            status="PENDING",
        )

    @patch("payments.views.virtual_bank_view.requests.post")
    def test_virtual_account_request_creates_payment(self, mock_post: Any, client: Any) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "paymentKey": "tviva20251106111111ABCDE",
            "virtualAccount": {
                "bank": "KOOKMIN",
                "accountNumber": "110-123-456789",
                "customerName": "홍길동",
                "dueDate": "2025-11-07T12:00:00+09:00"
            }
        }

        url = reverse("payments:toss-virtual-request")
        payload = {
            "orderId": self.order.order_id,
            "customerName": "홍길동",
            "bank": "KOOKMIN",
        }

        client.force_login(self.customer_user)
        res = client.post(url, json.dumps(payload), content_type="application/json")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["orderId"] == self.order.order_id
        assert data["bank"] == "KOOKMIN"
        assert "account_number" in data
        assert "due_date" in data

        # DB 검증
        payment = Payment.objects.filter(order=self.order).first()
        assert payment is not None
        assert payment.status == "WAITING_FOR_DEPOSIT"
        assert payment.method == "VIRTUAL_ACCOUNT"
        assert payment.account_number == "110123456789"  # 숫자만 저장 확인
        assert payment.bank_name == "KOOKMIN"
        assert payment.account_holder == "홍길동"

    def test_virtual_account_webhook_deposit_done(self, client: Any) -> None:
        payment = Payment.objects.create(
            order=self.order,
            provider="toss",
            method="VIRTUAL_ACCOUNT",
            payment_key="tviva20251106111111ABCDE",
            amount=self.order.total_amount,
            bank_name="KOOKMIN",
            account_number="110123456789",
            account_holder="홍길동",
            status="WAITING_FOR_DEPOSIT",
        )

        url = reverse("payments:toss-virtual-webhook")
        payload = {
            "paymentKey": payment.payment_key,
            "orderId": self.order.order_id,
            "status": "DONE",
        }

        res = client.post(url, json.dumps(payload), content_type="application/json")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["message"] == "입금 완료 처리됨"

        payment.refresh_from_db()
        self.order.refresh_from_db()
        assert payment.status == "APPROVED"
        assert self.order.status == "PAID"
        assert payment.approved_at is not None

    def test_virtual_account_webhook_invalid_payment_key(self, client: Any) -> None:
        url = reverse("payments:toss-virtual-webhook")
        payload = {
            "paymentKey": "invalid_key_999",
            "orderId": self.order.order_id,
            "status": "DONE",
        }

        res = client.post(url, json.dumps(payload), content_type="application/json")
        assert res.status_code == 404
        data = res.json()
        assert "error" in data
