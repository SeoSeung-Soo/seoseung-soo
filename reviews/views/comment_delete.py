from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from products.utils.url_slug import product_name_to_slug
from reviews.models import ReviewComment
from users.utils.permission import AdminPermission


class ReviewCommentDeleteView(AdminPermission, View):
    login_url = '/users/login/'

    def post(self, request: HttpRequest, comment_id: int) -> HttpResponse:
        comment = get_object_or_404(ReviewComment, id=comment_id)

        product_name = comment.review.product.name
        comment.delete()

        return redirect('products-detail', product_name=product_name_to_slug(product_name))