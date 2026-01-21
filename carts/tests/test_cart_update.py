import pytest
from django.urls import reverse

from carts.forms.update import CartUpdateForm  # 실제 경로에 맞게 조정
from carts.models import Cart
from config.utils.setup_test_method import TestSetupMixin


@pytest.mark.django_db
class TestCartUpdate(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.client.force_login(self.customer_user)

    def test_form_valid_quantity(self) -> None:
        form = CartUpdateForm(data={'quantity': 3})
        assert form.is_valid()
        assert form.cleaned_data['quantity'] == 3

    def test_form_quantity_is_zero(self) -> None:
        form = CartUpdateForm(data={'quantity': 0})
        assert not form.is_valid()
        assert 'quantity' in form.errors
        assert form.errors['quantity'] == ['수량은 1개 이상이어야 합니다.']

    def test_form_quantity_is_negative(self) -> None:
        form = CartUpdateForm(data={'quantity': -5})
        assert not form.is_valid()
        assert 'quantity' in form.errors
        assert form.errors['quantity'] == ['수량은 1개 이상이어야 합니다.']

    def test_cart_update_success(self) -> None:
        cart_item = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=1,
        )
        self.product.stock = 10
        self.product.save()

        url = reverse("cart-update", kwargs={"cart_id": cart_item.id})
        response = self.client.post(url, data={"quantity": 3})

        assert response.status_code == 302
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_cart_update_stock_insufficient_redirects(self) -> None:
        cart_item = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=1,
        )
        self.product.stock = 2
        self.product.save()

        url = reverse("cart-update", kwargs={"cart_id": cart_item.id})
        response = self.client.post(url, data={"quantity": 5})

        assert response.status_code == 302
        cart_item.refresh_from_db()
        assert cart_item.quantity == 1

    def test_cart_update_invalid_form_redirects(self) -> None:
        cart_item = Cart.objects.create(
            user=self.customer_user,
            product=self.product,
            quantity=1,
        )

        url = reverse("cart-update", kwargs={"cart_id": cart_item.id})
        response = self.client.post(url, data={"quantity": 0})

        assert response.status_code == 302
        cart_item.refresh_from_db()
        assert cart_item.quantity == 1