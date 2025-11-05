from typing import cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from products.utils.url_slug import product_name_to_slug
from reviews.forms.review_create import ReviewCommentForm
from reviews.models import Review
from users.models import User
from users.utils.permission import AdminPermission


class ReviewCommentCreateView(AdminPermission, View):

    def post(self, request: HttpRequest, review_id: int) -> HttpResponse:
        review = get_object_or_404(Review, id=review_id)
        form = ReviewCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = cast(User, request.user)
            comment.review = review
            comment.save()

        return redirect('products-detail', product_name=product_name_to_slug(review.product.name))

