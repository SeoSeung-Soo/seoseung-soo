import json
from typing import Any, Dict
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from orders.models import Order
from payments.models import Payment, PaymentLog
from users.models import User


class TestTossPaymentViews(TestCase):
    """Toss 결제 관련 API 단위 테스트"""

    client: Client
    order: Order

    def setUp(self) -> None:
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email="testuser@example.com",
            password="test1234!",
            personal_info_consent=True,
            terms_of_use=True,
        )

        # 임시 주문 생성
        self.order = Order.objects.create(
            user=self.user,
            order_id="ORD-20251104000000-TEST01",
            product_name="테스트 상품",
            total_amount=35000,
            status="PENDING",
        )

    def test_toss_payment_request_success(self) -> None:
        """결제 요청이 성공적으로 주문 정보를 반환하는지 검증"""
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
        """Toss 결제 승인 API가 성공적으로 결제 데이터를 저장하는지 검증"""
        mock_response: Dict[str, Any] = {
            "method": "CARD",
            "totalAmount": 35000,
            "receipt": {"url": "https://sandbox.tosspayments.com/receipt/test"},
        }

        # requests.post()를 mock 처리
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        url = reverse("payments:toss-confirm")
        params: Dict[str, str] = {
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

        # DB에 Payment, PaymentLog 생성 확인
        payment = Payment.objects.filter(order=self.order).first()
        assert payment is not None
        assert payment.status == "APPROVED"
        assert int(payment.amount) == 35000
        assert payment.receipt_url == "https://sandbox.tosspayments.com/receipt/test"

        log = PaymentLog.objects.filter(provider="toss").first()
        assert log is not None
        assert log.status_code == 200

    @patch("payments.views.toss_view.requests.post")
    def test_toss_confirm_failure(self, mock_post: Any) -> None:
        """Toss 결제 승인 실패 시 올바른 오류 응답을 반환하는지 검증"""
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "message": "잘못된 시크릿키 연동 정보 입니다."
        }

        url = reverse("payments:toss-confirm")
        params: Dict[str, str] = {
            "paymentKey": "tviva20251104024801IO5C8",
            "orderId": self.order.order_id,
            "amount": "35000",
        }
        response = self.client.get(url, params)

        data: Dict[str, Any] = response.json()
        assert response.status_code == 400
        assert data["success"] is False
        assert "잘못된 시크릿키" in data["error"]
