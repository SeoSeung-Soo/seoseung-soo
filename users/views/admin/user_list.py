from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from config.utils.filtering import Filtering
from users.utils.permission import AdminPermission


class AdminUserListView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        users_qs = Filtering.user_list_filter(request)

        paginator = Paginator(users_qs, 20)
        page_obj = paginator.get_page(request.GET.get("page") or "1")

        context = {
            "q": request.GET.get("q") or "",
            "role": request.GET.get("role") or "",
            "page_obj": page_obj,
            "users": page_obj.object_list,
        }
        return render(request, "users/admin/user_list.html", context)
