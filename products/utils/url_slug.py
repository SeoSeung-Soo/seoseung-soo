from typing import Optional

from django.utils.text import slugify

from products.models import Product


def product_name_to_slug(product_name: str) -> str:
    return slugify(product_name, allow_unicode=True)


def find_product_by_slug(slug: str) -> Optional[Product]:
    if not slug:
        return None
    
    return Product.objects.prefetch_related('colors').filter(slug=slug).first()
