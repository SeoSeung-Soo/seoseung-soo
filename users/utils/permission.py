from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest

from users.models import User


class AdminPermission(UserPassesTestMixin, LoginRequiredMixin):
    request: HttpRequest
    
    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        return user.is_authenticated and user.role == 'admin'

class CustomerPermission(UserPassesTestMixin, LoginRequiredMixin):
    request: HttpRequest

    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        return user.is_authenticated and user.role == 'customer' and user.role == 'admin'
