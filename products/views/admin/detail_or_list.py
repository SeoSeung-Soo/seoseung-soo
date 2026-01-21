from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from products.models import Product
from users.utils.permission import AdminPermission


class AdminMypageView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'title': '관리자 페이지'
        }
        return render(request, 'users/admin/mypage_admin.html', context)

class AdminProductListView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = Product.objects.all().order_by('-created_at')
        context = {
            'products': products,
            'title': '상품 목록'
        }
        return render(request, 'products/admin/admin_product_list.html', context)