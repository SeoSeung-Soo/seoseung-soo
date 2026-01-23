from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from config.utils.filtering import Filtering
from users.utils.permission import AdminPermission


class AdminOrderListView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        orders_qs = Filtering.order_list_filter(request)

        paginator = Paginator(orders_qs, 20)
        page_obj = paginator.get_page(request.GET.get("page") or "1")

        context = {
            "q": request.GET.get("q") or "",
            "status": request.GET.get("status") or "",
            "page_obj": page_obj,
            "orders": page_obj.object_list,
        }
        return render(request, "orders/admin/order_list.html", context)
