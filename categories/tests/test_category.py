import pytest
from django.urls import reverse

from categories.models import Category
from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestCategories(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()

    def test_create_category(self) -> None:
        url = reverse("category-list")
        self.client.force_login(self.admin_user)
        form_data = {
            "name": "대분류",
            "parent": ""
        }
        response = self.client.post(url, form_data)
        assert response.status_code == 302
        assert Category.objects.filter(name="대분류", parent=None).exists()

    def test_create_category_with_invalid_data(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("category-list")

        invalid_form_data = {
            "name": "",
            "parent": ""
        }

        response = self.client.post(url, invalid_form_data)

        assert response.status_code == 200

        assert 'form' in response.context
        form = response.context['form']
        assert not form.is_valid()
        assert 'name' in form.errors

        assert 'main_categories' in response.context

    def test_delete_category(self) -> None:
        self.client.force_login(self.admin_user)
        category = Category.objects.create(name="카테고리 삭제 데이터", parent=None)
        url = reverse("category-delete", args=[category.id])

        response = self.client.post(url)

        assert response.status_code == 302
        assert not Category.objects.filter(id=category.id).exists()

