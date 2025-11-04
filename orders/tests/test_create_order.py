from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict

import pytest
from django.test import Client
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestCreateOrderView(TestSetupMixin):

    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.client = Client()

    def test_requires_authentication(self) -> None:
        response = self.client.post(reverse("orders:create"))
        assert response.status_code == 401
        data = response.json()
        assert "로그인이 필요합니다." in data["error"]

    def test_invalid_json(self) -> None:
        self.client.force_login(self.customer_user)
        response = self.client.post(
            reverse("orders:create"),
            data="{invalid_json}",
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "잘못된 JSON 형식" in response.json()["error"]

    def test_create_order_success(self) -> None:
        self.client.force_login(self.customer_user)

        self.product.price = 35000
        self.product.save()

        payload: Dict[str, Any] = {
            "items": [
                {
                    "product_id": self.product.id,
                    "product_name": self.product.name,
                    "unit_price": int(self.product.price),
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post(
            reverse("orders:create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert "orderId" in data
        assert Decimal(str(data["amount"])) == Decimal("70000.00")

        order = Order.objects.get(order_id=data["orderId"])
        assert order.user == self.customer_user
        assert order.total_amount == 70000
        assert order.status == "PENDING"

        items = OrderItem.objects.filter(order=order)
        assert items.count() == 1

        item = items.first()
        assert item is not None
        assert item.product_id == self.product.id
        assert item.quantity == 2
        assert int(item.unit_price) == 35000
