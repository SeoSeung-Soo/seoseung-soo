from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from products.forms.product_color import ProductColorForm
from products.models import Color
from users.utils.permission import AdminPermission


class AdminProductColorView(AdminPermission, View):
    def get(self, request):
        colors = Color.objects.all().order_by('name')
        form = ProductColorForm()
        context = {
            'form': form,
            'colors': colors,
            'title': '색상 관리'
        }
        return render(request, 'products/admin/product_color.html', context)
    
    def post(self, request):
        form = ProductColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '색상이 성공적으로 생성되었습니다.')
            return redirect('admin-product-color')
        else:
            colors = Color.objects.all().order_by('name')
            context = {
                'form': form,
                'colors': colors,
                'title': '색상 관리'
            }
            messages.error(request, '색상 생성 중 오류가 발생했습니다.')
            return render(request, 'products/admin/product_color.html', context)


class AdminColorUpdateView(AdminPermission, View):
    def get(self, request, pk):
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
    
    def post(self, request, pk):
        color = get_object_or_404(Color, pk=pk)
        form = ProductColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, '색상이 성공적으로 수정되었습니다.')
            return redirect('admin-product-color')
        else:
            colors = Color.objects.all().order_by('name')
            context = {
                'form': form,
                'colors': colors,
                'color': color,
                'title': '색상 수정'
            }
            messages.error(request, '색상 수정 중 오류가 발생했습니다.')
            return render(request, 'products/admin/product_color.html', context)


class AdminColorDeleteView(AdminPermission, View):
    def post(self, request, pk):
        color = get_object_or_404(Color, pk=pk)
        color_name = color.name
        color.delete()
        messages.success(request, f'"{color_name}" 색상이 삭제되었습니다.')
        return redirect('admin-product-color')
