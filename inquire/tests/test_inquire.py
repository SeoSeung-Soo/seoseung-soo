import json
from unittest.mock import patch

import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from users.models import User


@pytest.mark.django_db
class TestInquire(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()

    def test_inquire_post_view_invalid_data(self) -> None:
        url = reverse("inquire")
        response = self.client.post(url, data={}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(response.content)
        assert response.status_code == 200
        assert data['success'] is False
        assert '입력한 정보를 확인해주세요' in data['message']

    def test_inquire_post_view_authenticated_user(self) -> None:
        url = reverse("inquire")
        self.client.force_login(self.customer_user)

        data = {
            'title': '문의 제목',
            'content': '문의 내용',
            'item': 'delivery',
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True

    def test_post_email_in_data_for_anonymous_user(self) -> None:
        url = reverse("inquire")
        data = {
            'title': '제목',
            'content': '내용',
            'item': 'etc',
            'email': 'guest@example.com',
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True

    def test_post_process_inquire_failure(self) -> None:
        url = reverse("inquire")
        self.client.force_login(self.customer_user)

        data = {
            'title': '문의 제목',
            'content': '문의 내용',
            'item': 'delivery',
        }

        with patch('inquire.services.inquire_user_valid.InquireUserValidService.process_inquire',
                   return_value=(False, "실패 메시지")):
            response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            assert response.status_code == 200
            result = json.loads(response.content)
            assert result['success'] is False
            assert result['message'] == "실패 메시지"

    def test_post_inquire_user_without_email(self) -> None:
        user = User.objects.create_user(
            username="noemailuser",
            password="pass1234",
            email="",
            personal_info_consent=True,
            terms_of_use=True,
        )
        self.client.force_login(user)

        url = reverse("inquire")
        data = {
            'title': '문의 제목',
            'content': '문의 내용',
            'item': 'delivery',
        }

        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is False
        assert '이메일 주소를 입력해주세요' in result['message']
