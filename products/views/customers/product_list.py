from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from categories.models import Category
from products.models import Product


class ProductListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = Product.objects.filter(is_live=True, is_sold=False).prefetch_related('colors', 'image', 'categories').order_by('-created_at')
        
        search_query = request.GET.get('search', '')
        category_name = request.GET.get('category', '')
        selected_category = None
        
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(categories__name__icontains=search_query)
            ).distinct()
        
        if category_name:
            try:
                selected_category = Category.objects.get(name=category_name)
                products = products.filter(categories=selected_category)
            except Category.DoesNotExist:
                pass
        
        context = {
            'products': products,
            'search_query': search_query,
            'category': selected_category,
        }
        return render(request, 'products/customers/product_list.html', context)