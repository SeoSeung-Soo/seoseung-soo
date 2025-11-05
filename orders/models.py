from typing import Any

from django.conf import settings
from django.db import models

from products.models import Color


class Order(models.Model):
    """주문 기본 정보"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=64, unique=True)
    product_name = models.CharField(max_length=255)
    total_amount = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "결제대기"),
            ("PAID", "결제완료"),
            ("CANCELLED", "결제취소"),
            ("FAILED", "결제실패"),
        ],
        default="PENDING",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"[{self.order_id}] {self.user} ({self.status})"


class OrderItem(models.Model):
    """주문 상세 항목"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # 자동으로 subtotal 계산
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product_name} x {self.quantity}"
