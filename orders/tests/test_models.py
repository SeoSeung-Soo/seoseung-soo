import pytest

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrderModel(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_order_str(self) -> None:
        order_str = str(self.order)
        assert self.order.order_id in order_str
        assert str(self.order.user) in order_str
        assert self.order.status in order_str


@pytest.mark.django_db
class TestOrderItemModel(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_order_item_save_calculates_subtotal(self) -> None:
        order_item = OrderItem.objects.create(
            order=self.order,
            product_id=self.product.id,
            product_name=self.product.name,
            quantity=3,
            unit_price=10000,
        )
        
        assert order_item.subtotal == 30000

    def test_order_item_str(self) -> None:
        order_item = OrderItem.objects.create(
            order=self.order,
            product_id=self.product.id,
            product_name=self.product.name,
            quantity=2,
            unit_price=5000,
        )
        
        order_item_str = str(order_item)
        assert self.product.name in order_item_str
        assert "2" in order_item_str
