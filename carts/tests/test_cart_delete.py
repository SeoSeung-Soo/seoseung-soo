import pytest
from django.urls import reverse

from carts.models import Cart
from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestCartDeleteView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.client.force_login(self.customer_user)

    def test_cart_delete_success(self) -> None:
        cart_item = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=1,
        )

        url = reverse("cart-delete", kwargs={"cart_id": cart_item.id})
        response = self.client.post(url)

        assert response.status_code == 302
        assert Cart.objects.filter(id=cart_item.id).exists() is False

    def test_cart_delete_other_user_404(self) -> None:
        cart_item = Cart.objects.create(
            user=self.admin_user,
            product=self.product,
            quantity=1,
        )

        url = reverse("cart-delete", kwargs={"cart_id": cart_item.id})
        response = self.client.post(url)

        assert response.status_code == 404

