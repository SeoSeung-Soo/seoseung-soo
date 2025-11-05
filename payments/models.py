from django.db import models

from orders.models import Order


class BankChoices(models.TextChoices):
    KOOKMIN = "KOOKMIN", "국민은행"
    SHINHAN = "SHINHAN", "신한은행"
    WOORI = "WOORI", "우리은행"
    HANA = "HANA", "하나은행"
    NH = "NH", "농협은행"
    IBK = "IBK", "기업은행"
    SC = "SC", "SC제일은행"
    SUHYUP = "SUHYUP", "수협은행"
    DAEGU = "DAEGU", "대구은행"
    BUSAN = "BUSAN", "부산은행"
    KYONGNAM = "KYONGNAM", "경남은행"
    GWANGJU = "GWANGJU", "광주은행"
    JEONBUK = "JEONBUK", "전북은행"
    JEJU = "JEJU", "제주은행"
    KAKAO = "KAKAO", "카카오뱅크"
    TOSSBANK = "TOSSBANK", "토스뱅크"


class Payment(models.Model):
    """PG 결제 정보"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")

    provider = models.CharField(  # PG사 구분
        max_length=20,
        choices=[
            ("toss", "토스페이"),
            ("kakao", "카카오페이"),
            ("payco", "페이코"),
            ("naver", "네이버페이"),
            ("bank", "무통장입금"),
        ],
    )

    method = models.CharField(  # 결제 수단
        max_length=30,
        choices=[
            ("CARD", "신용카드"),
            ("EASY_PAY", "간편결제"),
            ("TRANSFER", "계좌이체"),
            ("VBANK", "가상계좌"),
        ],
    )

    payment_key = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    approved_at = models.DateTimeField(null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("REQUESTED", "요청됨"),
            ("APPROVED", "승인됨"),
            ("CANCELLED", "취소됨"),
            ("FAILED", "실패"),
        ],
        default="REQUESTED",
    )

    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 무통장입금용 필드
    bank_name = models.CharField(
        max_length=20,
        choices=BankChoices.choices,
        blank=True,
        null=True,
        help_text="Toss API 은행 코드"
    )
    account_number = models.CharField(max_length=50, null=True, blank=True)
    account_holder = models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.provider.upper()} | {self.payment_key} ({self.status})"


class PaymentLog(models.Model):
    """PG 요청/응답 로그"""

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs",
        null=True,
        blank=True,
    )
    provider = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50)  # APPROVE / CANCEL / REFUND 등
    request_url = models.CharField(max_length=255, null=True, blank=True)
    request_payload = models.JSONField()
    response_payload = models.JSONField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.provider}] {self.event_type} ({self.status_code})"
