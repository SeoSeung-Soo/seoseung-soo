
import pytest
from django.urls import reverse

from config.utils.setup_test_method import TestSetupMixin
from users.models import User


@pytest.mark.django_db
class TestUserList(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()

        for i in range(30):
            User.objects.create_user(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password="testpass",
                role="customer",
                personal_info_consent=True,
                terms_of_use=True,
            )

    def test_user_list(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-user-list')
        response = self.client.get(url)

        assert response.status_code == 200

    def test_user_list_with_search_query(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-user-list')
        # 'user1' 검색 시 user1, user10~user19 총 11개가 매칭됨 (icontains)
        response = self.client.get(url, {'q': 'user1'})
        users = response.context['users']

        assert response.status_code == 200
        assert len(users) == 11  # user1, user10~user19
        assert all('user1' in user.username or 'user1' in user.email for user in users)

    def test_user_list_with_role_filter(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-user-list')
        response = self.client.get(url, {'role': 'customer'})

        assert response.status_code == 200
        users = response.context['users']
        assert all(user.role == 'customer' for user in users)
        assert len(users) <= 30  # admin_user는 제외되므로 최대 30명

    def test_user_list_with_search_and_role_filter(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse('admin-user-list')
        response = self.client.get(url, {'q': 'user1', 'role': 'customer'})

        assert response.status_code == 200
        users = response.context['users']
        assert all(user.role == 'customer' for user in users)
        assert all('user1' in user.username or 'user1' in user.email for user in users)
        # user1, user10~user19 중 customer만 (11개)
        assert len(users) == 11