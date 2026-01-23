import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestShippingManagement(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_shipping_management_list(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.get(url)

        assert response.status_code == 200
        assert "orders/admin/shipping_management.html" in [t.name for t in response.templates]
        assert response.context["q"] == ""
        assert response.context["shipping_status"] == ""
        orders = list(response.context["orders"])
        assert len(orders) > 0
        assert all(o.status == "PAID" for o in orders)

    def test_shipping_management_list_with_search_query(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.get(url, {"q": "123456"})

        assert response.status_code == 200
        assert response.context["q"] == "123456"
        orders = list(response.context["orders"])
        assert len(orders) > 0
        assert all("123456" in o.order_id for o in orders)

    def test_shipping_management_list_with_shipping_status_filter(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.get(url, {"shipping_status": "PENDING"})

        assert response.status_code == 200
        assert response.context["shipping_status"] == "PENDING"
        orders = list(response.context["orders"])
        assert len(orders) > 0
        assert all(o.shipping_status == "PENDING" for o in orders)

    def test_shipping_management_update_status(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.post(url, {
            "order_id": self.order.id,
            "shipping_status": "SHIPPING"
        })

        assert response.status_code == 302
        self.order.refresh_from_db()
        assert self.order.shipping_status == "SHIPPING"

    def test_shipping_management_update_status_missing_order_id(self) -> None:
        from django.contrib.messages import get_messages
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.post(url, {
            "shipping_status": "SHIPPING"
        }, follow=True)

        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert any("주문 ID와 배송 상태를 모두 입력해주세요" in str(msg) for msg in messages)

    def test_shipping_management_update_status_missing_shipping_status(self) -> None:
        from django.contrib.messages import get_messages
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.post(url, {
            "order_id": self.order.id
        }, follow=True)

        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert any("주문 ID와 배송 상태를 모두 입력해주세요" in str(msg) for msg in messages)

    def test_shipping_management_update_status_to_delivered(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.post(url, {
            "order_id": self.order.id,
            "shipping_status": "DELIVERED"
        })

        assert response.status_code == 302
        self.order.refresh_from_db()
        assert self.order.shipping_status == "DELIVERED"

    def test_shipping_management_update_status_invalid_status(self) -> None:
        from django.contrib.messages import get_messages
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-shipping-management")

        response = self.client.post(url, {
            "order_id": self.order.id,
            "shipping_status": "INVALID_STATUS"
        }, follow=True)

        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert any("유효하지 않은 배송 상태입니다" in str(msg) for msg in messages)
        self.order.refresh_from_db()
        assert self.order.shipping_status == "PENDING"