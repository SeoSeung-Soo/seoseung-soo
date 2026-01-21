from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from users.models import User
from users.utils.permission import AdminPermission


class UserListView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        q = (request.GET.get("q") or "").strip()
        role = (request.GET.get("role") or "").strip()
        page = request.GET.get("page") or "1"

        users_qs = User.objects.all().order_by("-date_joined")

        if q:
            users_qs = users_qs.filter(
                Q(email__icontains=q)
                | Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(phone_number__icontains=q)
            )

        if role:
            users_qs = users_qs.filter(role=role)

        paginator = Paginator(users_qs, 20)
        page_obj = paginator.get_page(page)

        context = {
            "q": q,
            "role": role,
            "page_obj": page_obj,
            "users": page_obj.object_list,
        }
        return render(request, "users/admin/user_list.html", context)
