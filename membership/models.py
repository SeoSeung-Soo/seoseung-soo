from config.basemodel import BaseModel
from django.db import models

from django.db.models import Sum

class Coupon(BaseModel):
    name = models.CharField(max_length=100)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'coupon'

class UsedCoupon(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="user_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'used_coupon'

class UserPoint(BaseModel):
    class PointType(models.TextChoices):
        # TODO : 포인트 사용시 적립은 없음 -> 트랜잭션 불필요 예정(사용 or 적립)
        EARN = "EARN", "적립"
        USE = "USE", "사용"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="points")
    point_type = models.CharField(max_length=10, choices=PointType.choices)
    amount = models.IntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    balance_after = models.IntegerField(default=0, verbose_name="최종 포인트 금액")
    related_order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "user_point"

    @staticmethod
    def get_user_balance(user):
        return UserPoint.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or 0