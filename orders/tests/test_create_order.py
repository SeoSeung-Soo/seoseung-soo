from __future__ import annotations

import json
from typing import Any, Dict

import pytest
from django.urls import reverse

from config.utils.cache_helper import CacheHelper
from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestCreateOrderView(TestSetupMixin):

    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_requires_authentication(self) -> None:
        response = self.client.post(reverse("orders:create"))
        assert response.status_code == 302

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
        """PreOrder(임시 주문 캐시) 생성 성공"""
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

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "preOrderKey" in data
        assert data["preOrderKey"].startswith("order:preorder:")
        assert data["amount"] == 70000
        assert len(data["items"]) == 1
        assert "orderId" not in data

        cached = CacheHelper.get(data["preOrderKey"])
        assert cached is not None
        assert cached["amount"] == 70000
        assert cached["user_id"] == self.customer_user.id
        assert len(cached["items"]) == 1
