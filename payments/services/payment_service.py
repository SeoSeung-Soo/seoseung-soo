from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from config.utils.cache_helper import CacheHelper
from products.models import Product


class PaymentService:
    @staticmethod
    def validate_cache_data(pre_order_key: str, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        cache_data = CacheHelper.get(pre_order_key)
        
        if not cache_data:
            return False, "주문 정보가 만료되었거나 유효하지 않습니다.", None
        
        if cache_data.get('user_id') != user_id:
            return False, "권한이 없습니다.", None
        
        return True, "", cache_data

    @staticmethod
    def calculate_shipping_fee(amount: Decimal) -> Decimal:
        return Decimal('0') if amount >= Decimal('50000') else Decimal('3000')

    @staticmethod
    def prepare_order_items_with_products(items_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Decimal]:
        product_ids = [item['product_id'] for item in items_data]
        
        products = Product.objects.filter(id__in=product_ids).prefetch_related('image', 'colors')
        products_dict = {product.id: product for product in products}
        
        order_items_with_products: List[Dict[str, Any]] = []
        actual_total = Decimal('0')
        
        for item_data in items_data:
            product = products_dict.get(item_data['product_id'])
            
            if product:
                if product.sale_price:
                    item_price = Decimal(str(product.price)) - Decimal(str(product.sale_price))
                else:
                    item_price = Decimal(str(product.price))
                
                item_total = item_price * Decimal(str(item_data['quantity']))
                actual_total += item_total
                
                order_items_with_products.append({
                    'item': item_data,
                    'product': product,
                })
            else:
                item_total = Decimal(str(item_data['unit_price'])) * Decimal(str(item_data['quantity']))
                actual_total += item_total
                
                order_items_with_products.append({
                    'item': item_data,
                    'product': None,
                })
        
        return order_items_with_products, actual_total

    @staticmethod
    def generate_order_name(items_data: List[Dict[str, Any]]) -> str:
        if len(items_data) == 1:
            product_name = items_data[0].get('product_name', '상품')
            return str(product_name) if product_name else '상품'
        product_name = items_data[0].get('product_name', '상품')
        return f"{str(product_name) if product_name else '상품'} 외 {len(items_data) - 1}건"

    @staticmethod
    def prepare_payment_context(
        pre_order_key: Optional[str],
        toss_client_key: str,
        user_id: int
    ) -> Dict[str, Any]:
        if not pre_order_key:
            return {
                'order': None,
                'order_items_with_products': [],
                'actual_total': 0,
                'shipping_fee': 0,
                'final_amount': 0,
                'TOSS_CLIENT_KEY': toss_client_key,
                'pre_order_key': None,
            }
        
        is_valid, error_message, cache_data = PaymentService.validate_cache_data(pre_order_key, user_id)
        
        if not is_valid or cache_data is None:
            return {
                'order': None,
                'order_items_with_products': [],
                'actual_total': 0,
                'shipping_fee': 0,
                'final_amount': 0,
                'TOSS_CLIENT_KEY': toss_client_key,
                'pre_order_key': None,
                'error': error_message,
            }
        
        items_data = cache_data.get('items', [])
        order_items_with_products, actual_total = PaymentService.prepare_order_items_with_products(items_data)
        shipping_fee = PaymentService.calculate_shipping_fee(actual_total)
        final_amount = actual_total + shipping_fee
        order_name = PaymentService.generate_order_name(items_data)
        
        return {
            'order': {
                'order_id': None,
                'product_name': order_name,
                'total_amount': int(actual_total),
            },
            'order_items_with_products': order_items_with_products,
            'actual_total': int(actual_total),
            'shipping_fee': int(shipping_fee),
            'final_amount': int(final_amount),
            'TOSS_CLIENT_KEY': toss_client_key,
            'pre_order_key': pre_order_key,
        }
