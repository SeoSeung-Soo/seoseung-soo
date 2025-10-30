import pytest

from config.utils.setup_test_method import TestSetupMixin
from products.forms.product_color import ProductColorForm
from products.models import Color


@pytest.mark.django_db
class TestColorForm(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()

    def test_hex_code_widget_value_with_instance(self) -> None:
        instance = Color.objects.create(name="Test", hex_code="#123456")
        form = ProductColorForm(instance=instance)
        assert form.fields['hex_code'].widget.attrs['value'] == "#123456"

    def test_hex_code_widget_value_with_data(self) -> None:
        data = {'hex_code': '#abcdef'}
        form = ProductColorForm(data=data)
        assert form.fields['hex_code'].widget.attrs['value'] == "#abcdef"

    def test_hex_code_widget_value_default(self) -> None:
        form = ProductColorForm()
        assert form.fields['hex_code'].widget.attrs['value'] == "#000000"