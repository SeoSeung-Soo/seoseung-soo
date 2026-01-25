import json
from typing import Any, Dict

import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order, OrderItem
from products.models import Color


@pytest.mark.django_db
class TestOrderCreateVirtualView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_requires_authentication(self) -> None:
        response = self.client.post(reverse("orders:virtual-create"))
        assert response.status_code == 302

    def test_invalid_json(self) -> None:
        self.client.force_login(self.customer_user)
        response = self.client.post(
            reverse("orders:virtual-create"),
            data="{invalid_json}",
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "잘못된 JSON 형식" in response.json()["error"]

    def test_create_virtual_order_success(self) -> None:
        self.client.force_login(self.customer_user)
        self.product.price = 35000
        self.product.save()

        payload: Dict[str, Any] = {
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post(
            reverse("orders:virtual-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "orderId" in data
        assert data["status"] == "PENDING"
        assert data["totalAmount"] == 70000

        order = Order.objects.get(order_id=data["orderId"])
        assert order.user == self.customer_user
        assert order.status == Order.Status.PENDING
        assert order.total_amount == 70000

        order_items = OrderItem.objects.filter(order=order)
        assert order_items.count() == 1
        order_item = order_items.first()
        assert order_item is not None
        assert order_item.quantity == 2

    def test_create_virtual_order_with_color(self) -> None:
        self.client.force_login(self.customer_user)
        self.product.price = 35000
        self.product.save()
        color = Color.objects.create(name="빨강", hex_code="#FF0000")
        self.product.colors.add(color)

        payload: Dict[str, Any] = {
            "items": [
                {
                    "product_id": self.product.id,
                    "color_id": color.id,
                    "quantity": 1,
                }
            ]
        }

        response = self.client.post(
            reverse("orders:virtual-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        order = Order.objects.get(order_id=data["orderId"])
        order_item = OrderItem.objects.filter(order=order).first()
        assert order_item is not None
        assert order_item.color == color

    def test_create_virtual_order_invalid_items(self) -> None:
        self.client.force_login(self.customer_user)

        payload: Dict[str, Any] = {
            "items": [
                {
                    "product_id": 99999,  # 존재하지 않는 상품
                    "quantity": 1,
                }
            ]
        }

        response = self.client.post(
            reverse("orders:virtual-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "존재하지 않는 상품" in data["error"]

    def test_create_virtual_order_empty_items(self) -> None:
        self.client.force_login(self.customer_user)

        payload: Dict[str, Any] = {
            "items": []
        }

        response = self.client.post(
            reverse("orders:virtual-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "주문 항목이 비어있습니다" in data["error"]
