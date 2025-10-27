"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import include, path

from config import settings
from users import urls as users_urls


def home(request: HttpRequest) -> HttpResponse:
    from products.models import Product
    products = Product.objects.filter(is_live=True, is_sold=False).order_by('-created_at')
    context = {'products': products}
    return render(request, 'home.html', context)

def payment(request: HttpRequest) -> HttpResponse:
    return render(request, 'payments/payment.html')
urlpatterns = [
    path('', home, name='home'),
    path('payment/', payment),
    path("users/", include(users_urls), name='users'),
    path("products/", include("products.urls"), name='products'),
    path("categories/", include("categories.urls"), name='categories'),
    path("reviews/", include("reviews.urls"), name='reviews'),
    path("inquire/", include("inquire.urls"), name='inquire'),
    path("carts/", include("carts.urls"), name='carts'),
    path("favorites/", include("favorites.urls"), name='favorites'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
