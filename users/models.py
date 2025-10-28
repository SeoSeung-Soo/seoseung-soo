from django.contrib.auth.models import AbstractUser
from django.db import models

from config.basemodel import BaseModel


# Create your models here.
class User(AbstractUser, BaseModel):
    class Gender(models.TextChoices):
        MALE = 'Male', "남자"
        FEMALE = "Female", "여자"
    class Role(models.TextChoices):
        ADMIN = 'admin', "관리자"
        CUSTOMER = 'customer', '소비자'
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=None, null=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_image = models.URLField(max_length=500, null=True, blank=True, verbose_name="프로필 이미지")
    personal_info_consent = models.BooleanField(verbose_name="개인정보수집")
    terms_of_use = models.BooleanField(verbose_name="이용약관")
    sns_consent_to_receive = models.BooleanField(null=True, blank=True, default=False, verbose_name="sns수신")
    email_consent_to_receive = models.BooleanField(null=True, blank=True, default=False, verbose_name="email수신")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

class PermissionAdmin(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'admin_permissions'

class PermissionCustomer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'customer_permissions'

class SocialUser(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"
        KAKAO = "kakao", "Kakao"
        NAVER = "naver", "Naver"
        APPLE = "apple", "Apple"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        verbose_name="연결된 유저",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    social_id = models.CharField(max_length=255, verbose_name="소셜 플랫폼 고유 ID")
    email = models.EmailField(null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "소셜 유저"
        verbose_name_plural = "소셜 유저 목록"
        constraints = [
            models.UniqueConstraint(fields=["provider", "social_id"], name="unique_provider_social_id")
        ]

    def __str__(self) -> str:
        return f"{self.provider}: {self.email or self.social_id}"