from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from categories.forms.category import CategoryForm
from categories.models import Category
from users.utils.permission import AdminPermission


class CategoryView(AdminPermission, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = CategoryForm()
        main_categories = Category.objects.filter(parent=None).prefetch_related('children')
        context = {
            'form': form,
            'main_categories': main_categories,
        }
        return render(request, "category/list_category.html", context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category-list')
        
        main_categories = Category.objects.filter(parent=None).prefetch_related('children')
        context = {
            'form': form,
            'main_categories': main_categories,
        }
        return render(request, "category/list_category.html", context)

class CategoryDeleteView(AdminPermission, View):
    def post(self, request: HttpRequest, category_id: int) -> HttpResponse:
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return redirect("category-list")