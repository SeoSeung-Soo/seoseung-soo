import pytest
from django.urls import reverse

from carts.forms.create import CartCreateForm
from carts.models import Cart
from config.utils.setup_test_method import TestSetupMixin
from products.models import Color


@pytest.mark.django_db
class TestCartCreate(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.client.force_login(self.customer_user)

        def create_cart_data(quantity:int) -> Cart:
            cart_data = Cart.objects.create(
                user=self.customer_user,
                product=self.product,
                quantity=quantity,
            )
            return cart_data

        self.create_cart_data = create_cart_data


    def test_products_added_customer_cart(self) -> None:
        data = {
            "product_id" : self.product.id,
            "quantity" : 1,
        }

        form = CartCreateForm(data=data)

        assert form.is_valid()

    def test_product_not_exist(self) -> None:
        invalid_product_id = 99999
        data = {
            "product_id": invalid_product_id,
            "quantity": 1,
        }

        form = CartCreateForm(data=data)

        assert not form.is_valid()
        assert "product_id" in form.errors
        assert form.errors["product_id"] == ["존재하지 않는 상품입니다."]

    def test_color_not_exist(self) -> None:
        invalid_color_id = 99999
        data = {
            "product_id": self.product.id,
            "quantity": 1,
            "color_id": invalid_color_id,
        }

        form = CartCreateForm(data=data)

        assert not form.is_valid()
        assert "color_id" in form.errors
        assert form.errors["color_id"] == ["존재하지 않는 색상입니다."]

    def test_color_valid(self) -> None:
        color = Color.objects.create(name="Black", hex_code="#000000")
        data = {
            "product_id": self.product.id,
            "quantity": 1,
            "color_id": color.id,
        }

        form = CartCreateForm(data=data)

        assert form.is_valid()

    def test_stock_insufficient_form_validation(self) -> None:
        self.product.stock = 1
        self.product.save()

        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }

        form = CartCreateForm(data=data)

        assert not form.is_valid()
        assert "quantity" in form.errors
        assert form.errors["quantity"] == ["재고가 부족합니다."]

    def test_added_new_cart_item(self) -> None:

        url = reverse('cart-create')
        data = {
            "product_id" : self.product.id,
            "quantity" : 1,
        }
        response = self.client.post(url, data=data)

        cart_item = Cart.objects.first()

        assert response.status_code == 302
        assert cart_item is not None
        assert cart_item.quantity == 1
        assert cart_item.product == self.product

    def test_added_over_cart_item(self) -> None:
        self.create_cart_data(quantity=2)
        self.product.stock = 3
        self.product.save()

        data = {
            "product_id": self.product.id,
            "quantity": 2,
            "product_name": self.product.name,
        }

        url = reverse("cart-create")
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        assert response.status_code == 200

        json_data = response.json()
        assert json_data["success"] is False
        assert "재고가 부족합니다" in json_data["message"]

        cart_item = Cart.objects.get(user=self.customer_user, product=self.product)
        assert cart_item.quantity == 2

    def test_existing_cart_item_update_ajax_success(self) -> None:
        self.create_cart_data(quantity=1)
        self.product.stock = 5
        self.product.save()

        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }

        url = reverse("cart-create")
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert "상품이 장바구니에 추가되었습니다" in json_data["message"]

        cart_item = Cart.objects.get(user=self.customer_user, product=self.product)
        assert cart_item.quantity == 3


    def test_form_validation_error_ajax(self) -> None:
        data = {
            "product_id": 99999,
            "quantity": 1,
        }

        url = reverse("cart-create")
        response = self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is False
        assert "존재하지 않는 상품입니다" in json_data["message"]

    def test_form_validation_error_non(self) -> None:
        data = {
            "product_id": 99999,  # 존재하지 않는 상품
            "quantity": 1,
            "product_name": "test_product",
        }

        url = reverse("cart-create")
        response = self.client.post(url, data=data)
        assert response.status_code == 302
        assert Cart.objects.count() == 0


    def test_stock_insufficient_non_ajax(self) -> None:
        self.create_cart_data(quantity=2)
        self.product.stock = 3
        self.product.save()

        data = {
            "product_id": self.product.id,
            "quantity": 2,
            "product_name": self.product.name,
        }

        url = reverse("cart-create")
        response = self.client.post(url, data=data)

        assert response.status_code == 302
        cart_item = Cart.objects.get(user=self.customer_user, product=self.product)
        assert cart_item.quantity == 2