from typing import Optional, Union

from django.contrib.auth.models import AnonymousUser
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from config.settings import EMAIL_HOST_USER
from inquire.models import Inquire
from users.models import User


class InquireUserValidService:
    @staticmethod
    def validate_inquire_user_valid(user: Union[User, AnonymousUser]) -> tuple[Optional[User], Optional[str]]:
        if user.is_authenticated:
            return user, user.email
        else:
            return None, None

    @staticmethod
    def create_inquire(
        user: Optional[User],
        email: str,
        title: str,
        content: str,
        item: str
    ) -> Inquire:
        inquire = Inquire.objects.create(
            user=user,
            email=email,
            title=title,
            content=content,
            item=item,
        )
        return inquire
    
    @staticmethod
    def send_inquire_email(
        user: Optional[User],
        email: str,
        title: str,
        content: str,
        item: str
    ) -> bool:
        try:
            context = {
                "user": user,
                "email": email,
                "title": title,
                "content": content,
                "item": item
            }
            
            html_content = render_to_string("inquire/inquire_template.html", context)
            
            if user and user.is_authenticated:
                user_identifier = user.get_username() or user.username
            else:
                user_identifier = email
            
            subject = f"[SeoSeung-Soo 문의] {title} - {user_identifier}"

            email_msg = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=EMAIL_HOST_USER,
                to=['seoseungsoo.cp@gmail.com'],
                reply_to=[email],
            )

            email_msg.content_subtype = "html"
            email_msg.send(fail_silently=False)
            return True
            
        except Exception:
            return False

    @staticmethod
    def process_inquire(
        user: Optional[User],
        email: str,
        title: str,
        content: str,
        item: str
    ) -> tuple[bool, str]:
        try:
            email_sent = InquireUserValidService.send_inquire_email(
                user=user,
                email=email,
                title=title,
                content=content,
                item=item
            )
            
            if not email_sent:
                return False, "이메일 전송에 실패했습니다."
            
            InquireUserValidService.create_inquire(
                user=user,
                email=email,
                title=title,
                content=content,
                item=item
            )
            
            return True, "문의가 성공적으로 전송되었습니다."
            
        except Exception as e:
            return False, f"문의 처리 중 오류가 발생했습니다: {str(e)}"