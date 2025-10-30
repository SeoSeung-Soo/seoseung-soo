from datetime import timedelta
from typing import Any, Dict

from django.http import HttpRequest
from django.utils import timezone

from products.models import Product


def new_products_context(request: HttpRequest) -> Dict[str, Any]:
    one_month_ago = timezone.now() - timedelta(days=30)
    
    new_products = Product.objects.filter(
        created_at__gte=one_month_ago,
        is_live=True,
        is_sold=False
    ).select_related().prefetch_related('image').order_by('-created_at')[:10]
    
    return {
        'new_products': new_products
    }

