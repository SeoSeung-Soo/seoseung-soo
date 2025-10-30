from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from products.forms.product_color import ProductColorForm
from products.models import Color
from users.utils.permission import AdminPermission


class AdminProductColorView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        colors = Color.objects.all().order_by('name')
        form = ProductColorForm()
        context = {
            'form': form,
            'colors': colors,
            'title': '색상 관리'
        }
        return render(request, 'products/admin/product_color.html', context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        form = ProductColorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-product-color')
        else:
            colors = Color.objects.all().order_by('name')
            context = {
                'form': form,
                'colors': colors,
                'title': '색상 관리'
            }
            return render(request, 'products/admin/product_color.html', context)


class AdminColorUpdateView(AdminPermission, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        color = get_object_or_404(Color, pk=pk)
        form = ProductColorForm(instance=color)
        colors = Color.objects.all().order_by('name')
        context = {
            'form': form,
            'colors': colors,
            'color': color,
            'title': '색상 수정'
        }
        return render(request, 'products/admin/product_color.html', context)
    
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        color = get_object_or_404(Color, pk=pk)
        form = ProductColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            return redirect('admin-product-color')
        else:
            colors = Color.objects.all().order_by('name')
            context = {
                'form': form,
                'colors': colors,
                'color': color,
                'title': '색상 수정'
            }
            return render(request, 'products/admin/product_color.html', context)


class AdminColorDeleteView(AdminPermission, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        color = get_object_or_404(Color, pk=pk)
        color.delete()
        return redirect('admin-product-color')
