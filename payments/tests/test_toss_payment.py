import json
import uuid
from typing import Any, Dict
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from config.utils.cache_helper import CacheHelper
from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order
from payments.models import Payment, PaymentLog


@pytest.mark.django_db(transaction=True)
class TestTossPaymentCacheFlow(TestSetupMixin):

    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_create_preorder_cache(self) -> None:
        self.client.force_login(self.customer_user)

        payload = {
            "items": [
                {"product_id": self.product.id, "quantity": 2},
            ]
        }

        url = reverse("orders:create")
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        data: Dict[str, Any] = response.json()
        assert response.status_code == 200
        assert data["success"] is True
        assert data["preOrderKey"].startswith("order:preorder:")

        # Redis에 캐시가 실제로 존재하는지 확인
        cached = CacheHelper.get(data["preOrderKey"])
        assert cached is not None
        assert cached["amount"] == int(self.product.price) * 2
        assert cached["user_id"] == self.customer_user.id

    @patch("payments.services.toss_payment_service.requests.post")
    def test_toss_confirm_creates_order_payment(self, mock_post: Any) -> None:
        self.client.force_login(self.customer_user)

        Payment.objects.all().delete()
        PaymentLog.objects.all().delete()
        Order.objects.all().delete()

        pre_order_key = "order:preorder:testkey123"
        product_amount = int(self.product.price)
        shipping_fee = 0 if product_amount >= 50000 else 3000
        final_amount = product_amount + shipping_fee
        
        CacheHelper.set(
            pre_order_key,
            {
                "user_id": self.customer_user.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "product_name": self.product.name,
                        "quantity": 1,
                        "unit_price": product_amount,
                    }
                ],
                "amount": product_amount,
                "created_at": timezone.now().isoformat(),
            },
            timeout=60 * 15,
        )

        mock_payment_key = f"mock_{uuid.uuid4().hex}_{int(timezone.now().timestamp())}"

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "method": "CARD",
            "paymentKey": mock_payment_key,
            "totalAmount": final_amount,
            "receipt": {"url": "https://sandbox.tosspayments.com/receipt/mock"},
        }

        url = reverse("payments:toss-confirm")
        params = {
            "paymentKey": mock_payment_key,
            "orderId": f"ORD-{uuid.uuid4().hex[:6].upper()}",
            "amount": str(final_amount),
            "preOrderKey": pre_order_key,
        }

        response = self.client.get(url, params)
        assert response.status_code == 302

        orders = Order.objects.filter(user=self.customer_user)
        assert orders.exists()
        
        order = orders.first()
        assert order is not None
        assert order.user == self.customer_user
        assert order.status == "PAID"

        payment = Payment.objects.filter(order=order).first()
        assert payment is not None
        assert payment.payment_key == mock_payment_key
        assert int(payment.amount) == final_amount

        log = PaymentLog.objects.filter(provider="toss").first()
        assert log is not None
        assert log.status_code == 200

        assert CacheHelper.get(pre_order_key) is None

    @patch("payments.services.toss_payment_service.requests.post")
    def test_toss_confirm_invalid_preorder_key_returns_400(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "ok"}

        self.client.force_login(self.customer_user)

        invalid_preorder_key = "order:preorder:nonexistent"
        url = reverse("payments:toss-confirm")
        params = {
            "paymentKey": f"mock_{uuid.uuid4().hex}",
            "orderId": f"ORD-{uuid.uuid4().hex[:6].upper()}",
            "amount": str(int(self.product.price)),
            "preOrderKey": invalid_preorder_key,
        }

        response = self.client.get(url, params)
        data: Dict[str, Any] = response.json()

        assert response.status_code == 400
        assert data["success"] is False
        assert "preOrderKey" in data["error"] or "만료" in data["error"]