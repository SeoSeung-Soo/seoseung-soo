import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from products.utils.url_slug import product_name_to_slug


@pytest.mark.django_db
class TestProductDetail(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_product_detail_get(self) -> None:
        self.client.force_login(self.customer_user)
        slug = product_name_to_slug("Test Product")
        url = reverse('products-detail', kwargs={'product_name': slug})
        response = self.client.get(url)

        assert response.status_code == 200
        assert 'products' in response.context
        assert response.context['products'] == self.product
        assert 'Test Product' in response.context['products'].name