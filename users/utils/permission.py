from typing import cast

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest

from users.models import User


class AdminPermission(UserPassesTestMixin):
    request: HttpRequest
    
    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        return user.is_authenticated and user.role == 'admin'

class CustomerPermission(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        return user.is_authenticated and user.role == 'customer'
