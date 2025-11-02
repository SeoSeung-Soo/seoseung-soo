from config.basemodel import BaseModel
from django.db import models

from users.models import User


class Coupon(BaseModel):
    name = models.CharField(max_length=100)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

class UsedCoupon(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(auto_now_add=True)