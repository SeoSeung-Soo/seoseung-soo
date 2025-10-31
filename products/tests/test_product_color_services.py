import pytest

from config.utils.setup_test_method import TestSetupMixin
from products.models import Color
from products.services.color import ColorService


@pytest.mark.django_db
class TestProductColorServices(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.color_red = Color.objects.create(name="Red", hex_code="#FF0000")
        self.color_black = Color.objects.create(name="Black", hex_code="#000000")

    def test_get_all_colors_service(self) -> None:
        data = ColorService.get_all_colors()
        
        assert data is not None
        assert len(data) == 2
        # order_by('name')
        assert data[0].name == "Black"
        assert data[0].hex_code == "#000000"
        assert data[1].name == "Red"
        assert data[1].hex_code == "#FF0000"

    def test_get_color_by_id(self) -> None:
        data = ColorService.get_color_by_id(self.color_red.id)
        assert data is not None
        assert data.name == "Red"

    def test_invalid_get_color_by_id(self) -> None:
        data = ColorService.get_color_by_id(-1)
        assert data is None

