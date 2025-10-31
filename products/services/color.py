from typing import List

from products.models import Color


class ColorService:
    @staticmethod
    def get_all_colors() -> List[Color]:
        return list(Color.objects.all().order_by('name'))
    
    @staticmethod
    def get_color_by_id(color_id: int) -> Color | None:
        try:
            return Color.objects.get(id=color_id)
        except Color.DoesNotExist:
            return None
