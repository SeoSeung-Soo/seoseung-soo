import pytest

from config.utils.setup_test_method import TestSetupMixin
from orders.services.order_services import OrderService
from products.models import Color


@pytest.mark.django_db
class TestOrderService(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_validate_products_invalid_product_id(self) -> None:
        is_valid, error_message, product_map = OrderService.validate_products([99999])
        
        assert is_valid is False
        assert "존재하지 않는 상품이 포함되어 있습니다" in error_message
        assert product_map == {}

    def test_validate_color_color_not_exists(self) -> None:
        is_valid, error_message = OrderService.validate_color(99999, self.product)
        
        assert is_valid is False
        assert "존재하지 않는 색상입니다" in error_message

    def test_validate_color_color_not_in_product(self) -> None:
        other_color = Color.objects.create(name="다른색상", hex_code="#000000")
        is_valid, error_message = OrderService.validate_color(other_color.id, self.product)
        
        assert is_valid is False
        assert f"'{self.product.name}' 상품에 선택하신 색상이 존재하지 않습니다" in error_message

    def test_calculate_item_price_with_sale_price(self) -> None:
        self.product.price = 10000
        self.product.sale_price = 2000
        self.product.save()
        
        price = OrderService.calculate_item_price(self.product)
        
        assert price == 8000

    def test_validate_and_prepare_order_items_empty_items(self) -> None:
        is_valid, error_message, validated_items, total_amount = OrderService.validate_and_prepare_order_items([])
        
        assert is_valid is False
        assert "주문 항목이 비어있습니다" in error_message
        assert validated_items == []
        assert total_amount == 0

    def test_validate_and_prepare_order_items_invalid_product(self) -> None:
        items_data = [{"product_id": 99999, "quantity": 1}]
        is_valid, error_message, validated_items, total_amount = OrderService.validate_and_prepare_order_items(items_data)
        
        assert is_valid is False
        assert "존재하지 않는 상품이 포함되어 있습니다" in error_message
        assert validated_items == []
        assert total_amount == 0

    def test_validate_and_prepare_order_items_invalid_color(self) -> None:
        other_color = Color.objects.create(name="다른색상", hex_code="#000000")
        items_data = [{"product_id": self.product.id, "color_id": other_color.id, "quantity": 1}]
        is_valid, error_message, validated_items, total_amount = OrderService.validate_and_prepare_order_items(items_data)
        
        assert is_valid is False
        assert "존재하지 않는 색상" in error_message or "선택하신 색상이 존재하지 않습니다" in error_message
        assert validated_items == []
        assert total_amount == 0
