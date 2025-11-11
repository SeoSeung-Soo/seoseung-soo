from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import View

from membership.models import UsedCoupon, UserPoint
from users.models import User


class ProfileEditView(LoginRequiredMixin, View):
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
        
        # 포인트 잔액 조회
        point_balance = UserPoint.get_user_balance(user)
        
        # 사용 가능한 쿠폰 개수 조회 (사용하지 않았고, 유효기간 내)
        today = timezone.now().date()
        available_coupons_count = UsedCoupon.objects.filter(
            user=user,
            is_used=False,
            coupon__is_active=True,
            coupon__start_date__lte=today,
            coupon__end_date__gte=today
        ).count()
        
        context = {
            'user': user,
            'point_balance': point_balance,
            'available_coupons_count': available_coupons_count,
        }
        return render(request, "users/mypage.html", context)