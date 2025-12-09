from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from membership.models import UsedCoupon, UserPoint
from users.models import User


class MembershipView(LoginRequiredMixin, View):
    """쿠폰과 적립금 통합 페이지"""

    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)

        # 포인트 내역 조회 (최신순)
        point_history = UserPoint.objects.filter(user=user).order_by('-created_at')
        point_balance = UserPoint.get_user_balance(user)

        # 사용 가능한 쿠폰 조회
        today = timezone.now().date()
        available_coupons = UsedCoupon.objects.filter(
            user=user,
            is_used=False,
            coupon__is_active=True,
            coupon__start_date__lte=today,
            coupon__end_date__gte=today
        ).select_related('coupon').order_by('-created_at')

        # 사용한 쿠폰 조회
        used_coupons = UsedCoupon.objects.filter(
            user=user,
            is_used=True
        ).select_related('coupon').order_by('-used_at')

        context = {
            'user': user,
            'point_history': point_history,
            'point_balance': point_balance,
            'available_coupons': available_coupons,
            'used_coupons': used_coupons,
        }
        return render(request, "membership/membership.html", context)