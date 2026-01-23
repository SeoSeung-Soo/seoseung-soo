import pytest
from django.urls import reverse

from carts.models import Cart
from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestCartDetailView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.client.force_login(self.customer_user)

    def test_cart_detail_total_price_no_sale_price(self) -> None:
        # price=5.00, sale_price=None, quantity=2 -> 10.00
        self.product.sale_price = None
        self.product.stock = 10
        self.product.save()
        Cart.objects.create(user=self.customer_user, product=self.product, quantity=2)

        url = reverse("cart-detail")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context["total_price"] == 10

    def test_cart_detail_total_price_with_sale_price(self) -> None:
        # view 로직: price - sale_price
        # price=5.00, sale_price=1.00, quantity=3 -> (5-1)*3=12.00
        self.product.sale_price = 1
        self.product.stock = 10
        self.product.save()
        Cart.objects.create(user=self.customer_user, product=self.product, quantity=3)

        url = reverse("cart-detail")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context["total_price"] == 12

