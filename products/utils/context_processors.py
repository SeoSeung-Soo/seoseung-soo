from datetime import timedelta
from typing import Any, Dict

from django.http import HttpRequest
from django.utils import timezone

from config.utils.cache_helper import CacheHelper
from products.models import Product

NEW_PRODUCT_PERIOD_DAYS = 30
NEW_PRODUCT_LIMIT = 10
NEW_PRODUCT_CACHE_TIMEOUT = 300


def new_products_context(request: HttpRequest) -> Dict[str, Any]:
    cache_key = 'product:new:list'
    
    product_ids = CacheHelper.get(cache_key)
    
    if product_ids is None:
        one_month_ago = timezone.now() - timedelta(days=NEW_PRODUCT_PERIOD_DAYS)
        
        products = Product.objects.filter(
            created_at__gte=one_month_ago,
            is_live=True,
            is_sold=False
        ).order_by('-created_at')[:NEW_PRODUCT_LIMIT]
        
        product_ids = [product.id for product in products]
        
        CacheHelper.set(cache_key, product_ids, NEW_PRODUCT_CACHE_TIMEOUT)
    
    if product_ids:
        products_dict = {
            p.id: p for p in Product.objects.filter(
                id__in=product_ids
            ).prefetch_related('colors', 'image')
        }
        new_products = [products_dict[pid] for pid in product_ids if pid in products_dict]
    else:
        new_products = []
    
    return {
        'new_products': new_products
    }

