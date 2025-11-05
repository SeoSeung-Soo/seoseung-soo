import os
from typing import Any
from unittest.mock import patch

import pytest

from carts.models import Cart
from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order, OrderItem
from payments.services.toss_payment_service import TossPaymentService
from products.models import Color


@pytest.mark.django_db
class TestTossPaymentService(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_get_toss_headers_success(self) -> None:
        with patch.dict(os.environ, {"TOSS_SECRET_KEY": "test_secret"}):
            headers = TossPaymentService.get_toss_headers()
            assert "Authorization" in headers
            assert "Content-Type" in headers
            assert headers["Content-Type"] == "application/json"

    def test_get_toss_headers_missing_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TOSS_SECRET_KEY"):
                TossPaymentService.get_toss_headers()

    def test_generate_order_id(self) -> None:
        order_id = TossPaymentService.generate_order_id()
        assert order_id.startswith("ORD-")
        assert len(order_id) > 10

    def test_generate_order_name_single(self) -> None:
        items_data = [{"product_name": "테스트 상품"}]
        name = TossPaymentService.generate_order_name(items_data)
        assert name == "테스트 상품"

    def test_generate_order_name_multiple(self) -> None:
        items_data = [
            {"product_name": "첫 번째 상품"},
            {"product_name": "두 번째 상품"},
        ]
        name = TossPaymentService.generate_order_name(items_data)
        assert "첫 번째 상품" in name
        assert "외 1건" in name

    def test_calculate_shipping_fee_free(self) -> None:
        fee = TossPaymentService.calculate_shipping_fee(50000)
        assert fee == 0

    def test_calculate_shipping_fee_paid(self) -> None:
        fee = TossPaymentService.calculate_shipping_fee(49999)
        assert fee == 3000

    def test_prepare_payment_request(self) -> None:
        pre_order_key = "order:preorder:test123"
        cache_data = {
            "items": [{"product_name": "테스트 상품"}],
            "amount": 30000,
        }
        base_url = "https://test.com"

        order_id, order_name, final_amount, response_data = (
            TossPaymentService.prepare_payment_request(pre_order_key, cache_data, base_url)
        )

        assert order_id.startswith("ORD-")
        assert order_name == "테스트 상품"
        assert final_amount == 33000
        assert response_data["success"] is True
        assert response_data["orderId"] == order_id
        assert response_data["amount"] == final_amount

    @patch("payments.services.toss_payment_service.requests.post")
    def test_confirm_payment_with_api_success(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"method": "CARD", "status": "ok"}

        with patch.dict(os.environ, {"TOSS_SECRET_KEY": "test_secret", "TOSS_API_BASE": "https://api.test.com"}):
            is_success, error_message, data, status_code = TossPaymentService.confirm_payment_with_api(
                payment_key="test_key",
                order_id="ORD-123",
                amount=10000
            )

            assert is_success is True
            assert error_message == ""
            assert status_code == 200

    @patch("payments.services.toss_payment_service.requests.post")
    def test_confirm_payment_with_api_failure(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"message": "결제 실패"}

        with patch.dict(os.environ, {"TOSS_SECRET_KEY": "test_secret", "TOSS_API_BASE": "https://api.test.com"}):
            is_success, error_message, data, status_code = TossPaymentService.confirm_payment_with_api(
                payment_key="test_key",
                order_id="ORD-123",
                amount=10000
            )

            assert is_success is False
            assert "결제 실패" in error_message
            assert status_code == 400

    @patch("payments.services.toss_payment_service.requests.post")
    def test_confirm_payment_with_api_exception(self, mock_post: Any) -> None:
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        with patch.dict(os.environ, {"TOSS_SECRET_KEY": "test_secret", "TOSS_API_BASE": "https://api.test.com"}):
            is_success, error_message, data, status_code = TossPaymentService.confirm_payment_with_api(
                payment_key="test_key",
                order_id="ORD-123",
                amount=10000
            )

            assert is_success is False
            assert "오류 발생" in error_message
            assert status_code == 503

    def test_validate_payment_amount_success(self) -> None:
        cache_data = {"amount": 30000}
        shipping_fee = TossPaymentService.calculate_shipping_fee(30000)
        final_amount = 30000 + shipping_fee

        is_valid, error_message = TossPaymentService.validate_payment_amount(cache_data, final_amount)

        assert is_valid is True
        assert error_message == ""

    def test_validate_payment_amount_mismatch(self) -> None:
        cache_data = {"amount": 30000}
        is_valid, error_message = TossPaymentService.validate_payment_amount(cache_data, 99999)

        assert is_valid is False
        assert "일치하지 않습니다" in error_message

    def test_create_order_and_payment_with_color(self) -> None:
        color = Color.objects.create(name="빨강", hex_code="#FF0000")
        self.product.colors.add(color)

        items_data = [
            {
                "product_id": self.product.id,
                "product_name": self.product.name,
                "quantity": 1,
                "unit_price": int(self.product.price),
                "color_id": color.id,
            }
        ]

        payment_data = {
            "method": "CARD",
            "receipt": {"url": "https://test.com/receipt"},
        }

        TossPaymentService.create_order_and_payment(
            order_id="ORD-TEST123",
            user_id=self.customer_user.id,
            items_data=items_data,
            amount=10000,
            payment_key="test_payment_key",
            payment_data=payment_data,
            request_url="https://api.test.com/confirm",
            request_payload={},
            response_status_code=200
        )

        order = Order.objects.filter(order_id="ORD-TEST123").first()
        assert order is not None
        assert order.status == "PAID"

        order_item = OrderItem.objects.filter(order=order).first()
        assert order_item is not None
        assert order_item.color == color

    def test_create_order_and_payment_without_color(self) -> None:
        items_data = [
            {
                "product_id": self.product.id,
                "product_name": self.product.name,
                "quantity": 1,
                "unit_price": int(self.product.price),
            }
        ]

        payment_data = {
            "method": "CARD",
            "receipt": {"url": "https://test.com/receipt"},
        }

        TossPaymentService.create_order_and_payment(
            order_id="ORD-TEST456",
            user_id=self.customer_user.id,
            items_data=items_data,
            amount=10000,
            payment_key="test_payment_key2",
            payment_data=payment_data,
            request_url="https://api.test.com/confirm",
            request_payload={},
            response_status_code=200
        )

        order = Order.objects.filter(order_id="ORD-TEST456").first()
        assert order is not None

        order_item = OrderItem.objects.filter(order=order).first()
        assert order_item is not None
        assert order_item.color is None

    def test_create_order_and_payment_invalid_color(self) -> None:
        items_data = [
            {
                "product_id": self.product.id,
                "product_name": self.product.name,
                "quantity": 1,
                "unit_price": int(self.product.price),
                "color_id": 99999,
            }
        ]

        payment_data = {
            "method": "CARD",
            "receipt": {"url": "https://test.com/receipt"},
        }

        TossPaymentService.create_order_and_payment(
            order_id="ORD-TEST789",
            user_id=self.customer_user.id,
            items_data=items_data,
            amount=10000,
            payment_key="test_payment_key3",
            payment_data=payment_data,
            request_url="https://api.test.com/confirm",
            request_payload={},
            response_status_code=200
        )

        order = Order.objects.filter(order_id="ORD-TEST789").first()
        assert order is not None

        order_item = OrderItem.objects.filter(order=order).first()
        assert order_item is not None
        assert order_item.color is None

    def test_clear_cart_after_payment_with_color(self) -> None:
        from carts.models import Cart
        color = Color.objects.create(name="파랑", hex_code="#0000FF")
        self.product.colors.add(color)

        cart = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=5,
            color=color
        )

        items_data = [
            {
                "product_id": self.product.id,
                "quantity": 2,
                "color_id": color.id,
            }
        ]

        TossPaymentService.clear_cart_after_payment(self.customer_user.id, items_data)

        cart.refresh_from_db()
        assert cart.quantity == 3

    def test_clear_cart_after_payment_without_color(self) -> None:
        cart = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=5,
            color=None
        )

        items_data = [
            {
                "product_id": self.product.id,
                "quantity": 2,
            }
        ]

        TossPaymentService.clear_cart_after_payment(self.customer_user.id, items_data)

        cart.refresh_from_db()
        assert cart.quantity == 3

    def test_clear_cart_after_payment_remove_item(self) -> None:
        cart = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=2,
            color=None
        )

        items_data = [
            {
                "product_id": self.product.id,
                "quantity": 2,
            }
        ]

        TossPaymentService.clear_cart_after_payment(self.customer_user.id, items_data)

        assert not Cart.objects.filter(id=cart.id).exists()

    def test_clear_cart_after_payment_multiple_items(self) -> None:
        cart1 = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=3,
            color=None
        )
        cart2 = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=2,
            color=None
        )

        items_data = [
            {
                "product_id": self.product.id,
                "quantity": 4,
            }
        ]

        TossPaymentService.clear_cart_after_payment(self.customer_user.id, items_data)

        assert not Cart.objects.filter(id=cart1.id).exists()
        cart2.refresh_from_db()
        assert cart2.quantity == 1

    def test_clear_cart_after_payment_no_product_id(self) -> None:
        items_data = [
            {
                "product_id": None,
                "quantity": 2,
            }
        ]

        TossPaymentService.clear_cart_after_payment(self.customer_user.id, items_data)

        assert True

