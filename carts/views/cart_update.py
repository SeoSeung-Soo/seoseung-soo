from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from carts.forms.update import CartUpdateForm
from carts.models import Cart


class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, cart_id: int) -> HttpResponse:
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        form = CartUpdateForm(request.POST)
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > cart_item.product.stock:
                messages.error(request, f'재고가 부족합니다. (현재 재고: {cart_item.product.stock}개)')
                return redirect('cart-detail')
            
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'수량이 {quantity}개로 변경되었습니다.')

            return redirect('cart-detail')
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, str(error))
        
        return redirect('cart-detail')
