from datetime import timedelta
from typing import Any, Dict

from django.core.cache import cache
from django.http import HttpRequest
from django.utils import timezone

from products.models import Product

NEW_PRODUCT_PERIOD_DAYS = 30
NEW_PRODUCT_LIMIT = 10
NEW_PRODUCT_CACHE_TIMEOUT = 300


def new_products_context(request: HttpRequest) -> Dict[str, Any]:
    cache_key = 'new_products_list'
    
    new_products = cache.get(cache_key)
    
    if new_products is None:
        one_month_ago = timezone.now() - timedelta(days=NEW_PRODUCT_PERIOD_DAYS)
        
        new_products = list(Product.objects.filter(
            created_at__gte=one_month_ago,
            is_live=True,
            is_sold=False
        ).prefetch_related('colors', 'image').order_by('-created_at')[:NEW_PRODUCT_LIMIT]) 
        
        cache.set(cache_key, new_products, NEW_PRODUCT_CACHE_TIMEOUT)
    
    return {
        'new_products': new_products
    }

