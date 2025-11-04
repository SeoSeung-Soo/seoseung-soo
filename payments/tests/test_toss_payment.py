import json
import uuid
from typing import Any, Dict
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order
from payments.models import Payment, PaymentLog


@pytest.mark.django_db(transaction=True)
class TestTossPaymentCacheFlow(TestSetupMixin):

    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        cache.clear()

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
        assert data["preOrderKey"].startswith("preorder:")

        # Redis에 캐시가 실제로 존재하는지 확인
        cached = cache.get(data["preOrderKey"])
        assert cached is not None
        assert cached["amount"] == int(self.product.price) * 2
        assert cached["user_id"] == self.customer_user.id

    @patch("payments.views.toss_view.requests.post")
    def test_toss_confirm_creates_order_payment(self, mock_post: Any) -> None:
        self.client.force_login(self.customer_user)

        Payment.objects.all().delete()
        PaymentLog.objects.all().delete()
        Order.objects.all().delete()

        pre_order_key = "preorder:testkey123"
        cache.set(
            pre_order_key,
            {
                "user_id": self.customer_user.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "product_name": self.product.name,
                        "quantity": 1,
                        "unit_price": int(self.product.price),
                    }
                ],
                "amount": int(self.product.price),
                "created_at": timezone.now().isoformat(),
            },
            timeout=60 * 15,
        )

        mock_payment_key = f"mock_{uuid.uuid4().hex}_{int(timezone.now().timestamp())}"

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "method": "CARD",
            "paymentKey": mock_payment_key,
            "totalAmount": int(self.product.price),
            "receipt": {"url": "https://sandbox.tosspayments.com/receipt/mock"},
        }

        url = reverse("payments:toss-confirm")
        params = {
            "paymentKey": mock_payment_key,
            "orderId": f"ORD-{uuid.uuid4().hex[:6].upper()}",
            "amount": str(int(self.product.price)),
            "preOrderKey": pre_order_key,
        }

        response = self.client.get(url, params)
        assert response.status_code == 200

        data: Dict[str, Any] = response.json()
        assert data["success"] is True
        assert data["paymentKey"] == mock_payment_key
        assert data["amount"] == int(self.product.price)

        order = Order.objects.filter(order_id=data["orderId"]).first()
        assert order is not None
        assert order.user == self.customer_user
        assert order.status == "PAID"

        payment = Payment.objects.filter(order=order).first()
        assert payment is not None
        assert payment.payment_key == mock_payment_key
        assert int(payment.amount) == int(self.product.price)

        log = PaymentLog.objects.filter(provider="toss").first()
        assert log is not None
        assert log.status_code == 200

        assert cache.get(pre_order_key) is None
