from typing import cast

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from users.models import User


# TODO : 데이터 연동 후 데이터 수정
@method_decorator(login_required, name='dispatch')
class OrderView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        
        #TODO: 주문 현황 데이터 (추후 Order 모델이 생기면 실제 데이터로 대체)
        order_stats = {
            'pending': 0,
            'preparing': 0,
            'shipping': 0,
            'delivered': 0,
        }
        
        #TODO: 소핑백 현황 (추후 Cart 모델이 생기면 실제 데이터로 대체)
        cart_stats = {
            'items': 0,
            'likes': 0,
            'reviews': 0,
        }
        
        context = {
            'user': user,
            'order_stats': order_stats,
            'cart_stats': cart_stats,
            'current_page': 'orders',
        }
        
        return render(request, "orders/order_mypage.html", context)
    
# TODO : 데이터 연동 후 데이터 수정
@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        
        context = {
            'user': user,
            'current_page': 'profile_edit'
        }
        
        return render(request, "users/profile_edit.html", context)

class MyPageView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        context = {
            'user': user,
        }
        return render(request, "users/mypage.html", context)