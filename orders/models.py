from typing import Any

from django.conf import settings
from django.db import models

from products.models import Color


class Order(models.Model):
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

    shipping_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "배송대기"),
            ("SHIPPING", "배송중"),
            ("DELIVERED", "배송완료"),
        ],
        default="PENDING",
    )

    cancellation_request_status = models.CharField(
        max_length=20,
        choices=[
            ("NONE", "없음"),
            ("PENDING", "취소요청"),
            ("APPROVED", "취소승인"),
            ("REJECTED", "취소거부"),
        ],
        default="NONE",
    )

    class CancellationReason(models.TextChoices):
        SIZE_MISMATCH = "SIZE_MISMATCH", "사이즈가 안 맞아요"
        NOT_LIKE_COLOR = "NOT_LIKE_COLOR", "색상이 마음에 안 들어요"
        NOT_LIKE_DESIGN = "NOT_LIKE_DESIGN", "디자인이 마음에 안 들어요"
        WRONG_PRODUCT = "WRONG_PRODUCT", "다른 상품이 왔어요"
        DEFECTIVE = "DEFECTIVE", "제품 불량이에요"
        WRONG_DELIVERY = "WRONG_DELIVERY", "배송 오류"
        SIMPLE_CHANGE_OF_MIND = "SIMPLE_CHANGE_OF_MIND", "단순히 마음 바뀜"
        TOO_EXPENSIVE = "TOO_EXPENSIVE", "너무 비싸서"
        NO_NEED_ANYMORE = "NO_NEED_ANYMORE", "필요 없어졌어요"
        OTHER = "OTHER", "기타"
    
    cancellation_reason = models.CharField(max_length=50, choices=CancellationReason.choices, null=True, blank=True)
    cancellation_requested_at = models.DateTimeField(null=True, blank=True, verbose_name="취소 요청 시간")
    cancellation_processed_at = models.DateTimeField(null=True, blank=True, verbose_name="취소 처리 시간")
    cancellation_admin_note = models.TextField(null=True, blank=True, verbose_name="관리자 메모")

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
