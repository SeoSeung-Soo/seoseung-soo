from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from users.models import User


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        
        context = {
            'user': user,
            'current_page': 'profile_edit'
        }
        
        return render(request, "users/profile_edit.html", context)


class MyPageView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        context = {
            'user': user,
        }
        return render(request, "users/mypage.html", context)