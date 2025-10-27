import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestFavoriteRender(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_favorite_render(self) -> None:
        self.client.force_login(self.customer_user)
        
        url = reverse('favorite-list')
        data = {
            "user": self.customer_user.id,
            "product": self.product.id,
            "is_active": True
        }
        response = self.client.get(url, data)
        assert response.status_code == 200