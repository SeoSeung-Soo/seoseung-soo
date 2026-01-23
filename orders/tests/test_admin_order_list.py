import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestAdminOrderList(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_admin_order_list(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-order-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert "orders/admin/order_list.html" in [t.name for t in response.templates]
        assert "page_obj" in response.context
        assert "orders" in response.context
        assert list(response.context["orders"]) == list(response.context["page_obj"].object_list)

