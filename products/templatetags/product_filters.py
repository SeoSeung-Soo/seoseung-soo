from typing import Union

from django import template

register = template.Library()

@register.filter
def discount_rate(price: Union[int, float], sale_price: Union[int, float]) -> int:
    if not price or not sale_price or price <= 0:
        return 0

    discount = ((price - sale_price) / price) * 100
    return round(discount)

@register.filter
def discount_amount(price: Union[int, float], sale_price: Union[int, float]) -> int:
    if not price or price <= 0 or sale_price is None or sale_price < 0:
        return 0

    return int(price - sale_price)

@register.filter
def intcomma(value: Union[int, float, str]) -> str:
    if value is None:
        return '0'
    
    if isinstance(value, str):
        try:
            value = float(value.replace(',', ''))
        except (ValueError, AttributeError):
            return str(value)
    
    try:
        value = int(value)
    except (ValueError, TypeError):
        return str(value)
    
    return f"{value:,}"