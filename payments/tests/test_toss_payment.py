import json
from typing import Any, Dict
from unittest.mock import patch

import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order
from payments.models import Payment, PaymentLog


@pytest.mark.django_db
class TestTossPaymentViews(TestSetupMixin):
    """Toss 결제 관련 API 테스트"""

    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

        # 임시 주문 생성
        self.order = Order.objects.create(
            user=self.customer_user,
            order_id="ORD-20251104000000-TEST01",
            product_name="테스트 상품",
            total_amount=35000,
            status="PENDING",
        )

    def test_toss_payment_request_success(self) -> None:
        url = reverse("payments:toss-request")

        response = self.client.post(
            url,
            data=json.dumps({"orderId": self.order.order_id}),
            content_type="application/json",
        )

        data: Dict[str, Any] = response.json()
        assert response.status_code == 200
        assert data["success"] is True
        assert data["orderId"] == self.order.order_id
        assert data["amount"] == 35000
        assert data["orderName"] == "테스트 상품"
        assert "successUrl" in data
        assert "failUrl" in data

    @patch("payments.views.toss_view.requests.post")
    def test_toss_confirm_success(self, mock_post: Any) -> None:
        """결제 승인 API: 정상 결제 승인 시 DB에 결제/로그 저장"""
        mock_response: Dict[str, Any] = {
            "method": "CARD",
            "totalAmount": 35000,
            "receipt": {"url": "https://sandbox.tosspayments.com/receipt/test"},
        }

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        url = reverse("payments:toss-confirm")
        params = {
            "paymentKey": "tviva20251104024801IO5C8",
            "orderId": self.order.order_id,
            "amount": "35000",
        }
        response = self.client.get(url, params)
        data: Dict[str, Any] = response.json()

        assert response.status_code == 200
        assert data["success"] is True
        assert data["orderId"] == self.order.order_id
        assert data["amount"] == 35000
        assert data["paymentKey"] == "tviva20251104024801IO5C8"

        payment = Payment.objects.filter(order=self.order).first()
        assert payment is not None
        assert payment.status == "APPROVED"
        assert int(payment.amount) == 35000
        assert payment.receipt_url == "https://sandbox.tosspayments.com/receipt/test"

        log = PaymentLog.objects.filter(provider="toss").first()
        assert log is not None
        assert log.status_code == 200
        assert log.event_type == "CONFIRM"

    @patch("payments.views.toss_view.requests.post")
    def test_toss_confirm_failure(self, mock_post: Any) -> None:
        """결제 승인 API: 시크릿키 오류 등 실패 응답 처리"""
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "message": "잘못된 시크릿키 연동 정보 입니다."
        }

        url = reverse("payments:toss-confirm")
        params = {
            "paymentKey": "tviva20251104024801IO5C8",
            "orderId": self.order.order_id,
            "amount": "35000",
        }

        response = self.client.get(url, params)
        data: Dict[str, Any] = response.json()

        assert response.status_code == 400
        assert data["success"] is False
        assert "잘못된 시크릿키" in data["error"]
