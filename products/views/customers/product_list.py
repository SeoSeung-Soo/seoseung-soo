from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.shortcuts import render

from categories.models import Category
from products.models import Product


class ProductListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = Product.objects.filter(is_live=True, is_sold=False).prefetch_related('colors', 'image', 'categories').order_by('-created_at')
        
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(categories__name__icontains=search_query)
            ).distinct()
        
        context = {
            'products': products,
            'search_query': search_query,
        }
        return render(request, 'products/customers/product_list.html', context)