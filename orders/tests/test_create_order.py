from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
class TestCreateOrderView:
    """주문 생성 API 테스트"""

    @pytest.fixture
    def user(self) -> Any:
        """테스트용 유저 생성"""
        # mypy는 기본 UserManager 시그니처(username 필수)를 기준으로 검증하므로,
        # 커스텀 User(email 기반)에서는 call-arg 무시 필요.
        return User.objects.create_user(
            username='testuser',
            email="test@example.com",
            password="test1234!",
            personal_info_consent=True,
            terms_of_use=True,
        )

    @pytest.fixture
    def product(self, user: Any) -> Product:
        """테스트용 상품 생성"""
        return Product.objects.create(
            user=user,
            name="테스트 향수",
            description="테스트용 향수입니다.",
            price=Decimal("35000.00"),
            stock=10,
            is_live=True,
        )

    def test_requires_authentication(self, client: Client) -> None:
        """비로그인 사용자는 401"""
        response = client.post(reverse("orders:create"))
        assert response.status_code == 401
        data = response.json()
        assert "로그인이 필요합니다." in data["error"]

    def test_invalid_json(self, client: Client, user: Any) -> None:
        """잘못된 JSON 형식은 400"""
        client.force_login(user)
        response = client.post(
            reverse("orders:create"),
            data="{invalid_json}",
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "잘못된 JSON 형식" in response.json()["error"]

    def test_create_order_success(
        self, client: Client, user: Any, product: Product
    ) -> None:
        """정상 주문 생성"""
        client.force_login(user)

        payload: Dict[str, Any] = {
            "items": [
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "unit_price": int(product.price),
                    "quantity": 2,
                }
            ]
        }

        response = client.post(
            reverse("orders:create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert "orderId" in data
        assert int(float(data["amount"])) == 70000

        order = Order.objects.get(order_id=data["orderId"])
        assert order.user == user
        assert order.total_amount == 70000
        assert order.status == "PENDING"

        items = OrderItem.objects.filter(order=order)
        assert items.count() == 1

        item = items.first()
        assert item is not None
        assert item.product_id == product.id
        assert item.quantity == 2
        assert item.unit_price == 35000
