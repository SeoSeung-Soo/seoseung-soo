import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrderView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_order_view_requires_login(self) -> None:
        url = reverse("orders:status")
        response = self.client.get(url)
        
        assert response.status_code == 302

    def test_order_view_with_shipping_orders(self) -> None:
        self.client.force_login(self.customer_user)
        self.order.user = self.customer_user
        self.order.status = Order.Status.PAID
        self.order.shipping_status = Order.ShippingStatus.PENDING
        self.order.cancellation_request_status = Order.CancellationRequestStatus.NONE
        self.order.exchange_refund_request_status = Order.ExchangeRefundRequestStatus.NONE
        self.order.save()
        
        OrderItem.objects.create(
            order=self.order,
            product_id=self.product.id,
            product_name=self.product.name,
            quantity=1,
            unit_price=10000,
        )
        
        url = reverse("orders:status")
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert "shipping_orders" in response.context
        assert "order_stats" in response.context
        assert "cancellation_exchange_refund_stats" in response.context

    def test_order_view_with_payment_success(self) -> None:
        self.client.force_login(self.customer_user)
        session = self.client.session
        session["payment_success"] = True
        session["order_id"] = "test123"
        session.save()
        
        url = reverse("orders:status")
        response = self.client.get(url)
        
        assert response.status_code == 200
        session = self.client.session
        assert "payment_success" not in session
        assert "order_id" not in session


@pytest.mark.django_db
class TestCancelRefundView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_cancel_refund_view_requires_login(self) -> None:
        url = reverse("orders:cancel-refund")
        response = self.client.get(url)
        
        assert response.status_code == 302

    def test_cancel_refund_view_with_orders(self) -> None:
        self.client.force_login(self.customer_user)
        self.order.user = self.customer_user
        self.order.cancellation_request_status = Order.CancellationRequestStatus.PENDING
        self.order.save()
        
        OrderItem.objects.create(
            order=self.order,
            product_id=self.product.id,
            product_name=self.product.name,
            quantity=1,
            unit_price=10000,
        )
        
        url = reverse("orders:cancel-refund")
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert "cancellation_exchange_refund_orders" in response.context
        assert "order_stats" in response.context
        assert "cancellation_exchange_refund_stats" in response.context

    def test_cancel_refund_view_with_product_attachment(self) -> None:
        self.client.force_login(self.customer_user)
        self.order.user = self.customer_user
        self.order.cancellation_request_status = Order.CancellationRequestStatus.PENDING
        self.order.save()
        
        order_item = OrderItem.objects.create(
            order=self.order,
            product_id=self.product.id,
            product_name=self.product.name,
            quantity=1,
            unit_price=10000,
        )
        
        url = reverse("orders:cancel-refund")
        response = self.client.get(url)
        
        assert response.status_code == 200
        orders = response.context["cancellation_exchange_refund_orders"]
        if orders:
            order = orders[0]
            assert hasattr(order, "items_list")
            if order.items_list:
                item = order.items_list[0]
                assert hasattr(item, "product")
                assert item.product is not None
