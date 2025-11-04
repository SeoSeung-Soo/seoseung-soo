from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from products.utils.url_slug import product_name_to_slug
from reviews.models import Review


class ReviewDeleteView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request: HttpRequest, review_id: int) -> HttpResponse:
        review = get_object_or_404(Review, id=review_id)

        # 본인의 리뷰인지 확인
        if review.user != request.user:
            raise Http404("권한이 없습니다.")

        product_name = review.product.name
        review.delete()

        return redirect('products-detail', product_name=product_name_to_slug(product_name))







