import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from products.models import Color


@pytest.mark.django_db
class TestProductColorViews(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.color = Color.objects.create(name="Red", hex_code="#FF0000")

    def test_admin_render_product_colors_page(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-product-color')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_admin_create_product_color(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-product-color')
        data = {
            'name': 'Test Product Color',
            'hex_code': '000000',
        }
        response = self.client.post(url, data)
        assert response.status_code == 302

    def test_post_color_form_invalid(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-product-color')
        invalid_data = {
            'name': ''
        }
        response = self.client.post(url, data=invalid_data)

        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_admin_color_update_get(self) -> None:
        self.client.force_login(self.admin_user)

        url = reverse('admin-color-update', kwargs={'pk': self.color.pk})
        response = self.client.get(url)

        assert response.status_code == 200

    def test_admin_update_product_color(self) -> None:
        self.client.force_login(self.admin_user)

        url = reverse('admin-color-update', kwargs={'pk': self.color.pk})
        data = {
            'name': 'Blue',
            'hex_code': '#0000FF'
        }

        response = self.client.post(url, data)

        assert response.status_code == 302

    def test_admin_invalid_data_update(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-color-update', kwargs={'pk': self.color.pk})
        data = {
            'name': '',
        }
        response = self.client.post(url, data)

        assert response.status_code == 200

    def test_admin_delete_product_color(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-color-delete', kwargs={'pk': self.color.pk})
        response = self.client.post(url)
        assert response.status_code == 302