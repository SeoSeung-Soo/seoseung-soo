from decimal import Decimal

import pytest

from config.utils.cache_helper import CacheHelper
from config.utils.setup_test_method import TestSetupMixin
from payments.services.payment_service import PaymentService


@pytest.mark.django_db
class TestPaymentService(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_validate_cache_data_success(self) -> None:
        pre_order_key = "order:preorder:test123"
        cache_data = {
            "user_id": self.customer_user.id,
            "items": [],
            "amount": 10000,
        }
        CacheHelper.set(pre_order_key, cache_data, timeout=300)

        is_valid, error_message, result = PaymentService.validate_cache_data(
            pre_order_key, self.customer_user.id
        )

        assert is_valid is True
        assert error_message == ""
        assert result == cache_data

    def test_validate_cache_data_not_found(self) -> None:
        is_valid, error_message, result = PaymentService.validate_cache_data(
            "order:preorder:nonexistent", self.customer_user.id
        )

        assert is_valid is False
        assert "만료되었거나 유효하지 않습니다" in error_message
        assert result is None

    def test_validate_cache_data_wrong_user(self) -> None:
        pre_order_key = "order:preorder:test123"
        cache_data = {
            "user_id": 999,
            "items": [],
            "amount": 10000,
        }
        CacheHelper.set(pre_order_key, cache_data, timeout=300)

        is_valid, error_message, result = PaymentService.validate_cache_data(
            pre_order_key, self.customer_user.id
        )

        assert is_valid is False
        assert "권한이 없습니다" in error_message
        assert result is None

    def test_calculate_shipping_fee_free(self) -> None:
        fee = PaymentService.calculate_shipping_fee(Decimal("50000"))
        assert fee == Decimal("0")

    def test_calculate_shipping_fee_paid(self) -> None:
        fee = PaymentService.calculate_shipping_fee(Decimal("49999"))
        assert fee == Decimal("3000")

    def test_prepare_order_items_with_products_with_sale_price(self) -> None:
        self.product.price = 30000
        self.product.sale_price = 5000
        self.product.save()

        items_data = [
            {
                "product_id": self.product.id,
                "quantity": 2,
                "unit_price": 30000,
            }
        ]

        items, total = PaymentService.prepare_order_items_with_products(items_data)

        assert len(items) == 1
        assert items[0]["product"] == self.product
        expected_total = (30000 - 5000) * 2
        assert total == Decimal(str(expected_total))

    def test_prepare_order_items_with_products_without_product(self) -> None:
        items_data = [
            {
                "product_id": 99999,
                "quantity": 2,
                "unit_price": 30000,
            }
        ]

        items, total = PaymentService.prepare_order_items_with_products(items_data)

        assert len(items) == 1
        assert items[0]["product"] is None
        assert total == Decimal("60000")

    def test_generate_order_name_single(self) -> None:
        items_data = [{"product_name": "테스트 상품"}]
        name = PaymentService.generate_order_name(items_data)
        assert name == "테스트 상품"

    def test_generate_order_name_multiple(self) -> None:
        items_data = [
            {"product_name": "첫 번째 상품"},
            {"product_name": "두 번째 상품"},
        ]
        name = PaymentService.generate_order_name(items_data)
        assert "첫 번째 상품" in name
        assert "외 1건" in name

    def test_generate_order_name_empty_name(self) -> None:
        items_data = [{"product_name": ""}]
        name = PaymentService.generate_order_name(items_data)
        assert name == "상품"

    def test_prepare_payment_context_no_preorder_key(self) -> None:
        context = PaymentService.prepare_payment_context(
            pre_order_key=None,
            toss_client_key="test_key",
            user_id=self.customer_user.id
        )

        assert context["order"] is None
        assert context["actual_total"] == 0
        assert context["pre_order_key"] is None

    def test_prepare_payment_context_invalid_preorder_key(self) -> None:
        context = PaymentService.prepare_payment_context(
            pre_order_key="order:preorder:invalid",
            toss_client_key="test_key",
            user_id=self.customer_user.id
        )

        assert context["order"] is None
        assert "error" in context

    def test_prepare_payment_context_success(self) -> None:
        pre_order_key = "order:preorder:test123"
        cache_data = {
            "user_id": self.customer_user.id,
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "unit_price": int(self.product.price),
                }
            ],
            "amount": int(self.product.price),
        }
        CacheHelper.set(pre_order_key, cache_data, timeout=300)

        context = PaymentService.prepare_payment_context(
            pre_order_key=pre_order_key,
            toss_client_key="test_key",
            user_id=self.customer_user.id
        )

        assert context["order"] is not None
        assert context["actual_total"] > 0
        assert context["pre_order_key"] == pre_order_key

