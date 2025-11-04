from typing import Any, Optional, cast

from django.utils.text import slugify

from products.models import Product


def product_name_to_slug(product_name: str) -> str:
    return slugify(product_name, allow_unicode=False)


def find_product_by_slug(products_queryset: Any, slug: str) -> Optional[Product]:
    if not slug:
        return None
    
    products = list(products_queryset)
    
    for product in products:
        if product_name_to_slug(product.name) == slug:
            return cast(Product, product)
    
    return None
