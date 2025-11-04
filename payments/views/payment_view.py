from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from orders.models import Order
from products.models import Product

@login_required
def payment(request: HttpRequest) -> HttpResponse:
    
    order_id = request.GET.get('order_id')
    
    toss_client_key = getattr(settings, 'TOSS_CLIENT_KEY', '')
    
    if order_id:
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        
        order_items_with_products = []
        actual_total = Decimal('0')
        
        for item in order.items.all():
            try:
                product = Product.objects.prefetch_related('image', 'colors').get(id=item.product_id)
                
                if product.sale_price:
                    item_price = Decimal(str(product.price)) - Decimal(str(product.sale_price))
                else:
                    item_price = Decimal(str(product.price))
                
                item_total = item_price * Decimal(str(item.quantity))
                actual_total += item_total
                
                order_items_with_products.append({
                    'item': item,
                    'product': product,
                })
            except Product.DoesNotExist:
                item_total = Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
                actual_total += item_total
                
                order_items_with_products.append({
                    'item': item,
                    'product': None,
                })
        
        shipping_fee = Decimal('0') if actual_total >= Decimal('50000') else Decimal('3000')
        final_amount = actual_total + shipping_fee
        
        context = {
            'order': order,
            'order_items': order.items.all(),
            'order_items_with_products': order_items_with_products,
            'actual_total': int(actual_total),
            'shipping_fee': int(shipping_fee),
            'final_amount': int(final_amount),
            'TOSS_CLIENT_KEY': toss_client_key,
        }
    else:
        context = {
            'order': None,
            'order_items': [],
            'order_items_with_products': [],
            'actual_total': 0,
            'shipping_fee': 0,
            'final_amount': 0,
            'TOSS_CLIENT_KEY': toss_client_key,
        }
    
    return render(request, 'payments/payment.html', context)

