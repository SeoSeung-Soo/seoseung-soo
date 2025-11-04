from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from favorites.forms.favorite import FavoriteForm
from favorites.models import Favorite
from favorites.services.favorite_service import FavoriteService
from products.utils.url_slug import product_name_to_slug
from users.models import User


class FavoriteView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        favorites = FavoriteService.get_user_favorites(user)
        context = {"favorites": favorites}
        return render(request, "favorites/favorite_mypage.html", context)


class FavoriteCreateView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        form = FavoriteForm(request.POST)
        user = cast(User, request.user)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            result = FavoriteService.toggle_favorite(user, product_id)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(result)
            else:
                if result['success']:
                    request.session['favorite_message'] = result['message']
                else:
                    request.session['favorite_error'] = result['message']
                product_name_from_post = request.POST.get('product_name', '')
                if product_name_from_post:
                    return redirect('products-detail', product_name=product_name_to_slug(product_name_from_post))
                return redirect('customer-product-list')
        else:
            error_message = "잘못된 요청입니다."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message,
                    'is_favorite': False
                })
            else:
                request.session['favorite_error'] = error_message
                product_name_from_post = request.POST.get('product_name', '')
                if product_name_from_post:
                    return redirect('products-detail', product_name=product_name_to_slug(product_name_from_post))
                return redirect('customer-product-list')


class FavoriteDeleteView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)

        favorite_id = request.POST.get('favorite_id')
        if favorite_id:
            try:
                favorite = Favorite.objects.get(id=favorite_id, user=user)
                favorite.is_active = False
                favorite.save()

                result = {
                    'success': True,
                    'message': '찜목록에서 제거되었습니다.',
                    'is_active': False
                }
            except Favorite.DoesNotExist:
                result = {
                    'success': False,
                    'message': '찜한 상품을 찾을 수 없습니다.',
                    'is_active': False
                }
        else:
            form = FavoriteForm(request.POST)
            if form.is_valid():
                product_id = form.cleaned_data['product_id']
                result = FavoriteService.remove_from_favorites(user, product_id)
            else:
                result = {
                    'success': False,
                    'message': '잘못된 요청입니다.',
                    'is_active': False
                }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(result)
        else:
            if result['success']:
                request.session['favorite_message'] = result['message']
            else:
                request.session['favorite_error'] = result['message']
            return redirect('favorite-list')