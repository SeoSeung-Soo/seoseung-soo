
from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from products.models import Product
from products.utils.url_slug import product_name_to_slug
from reviews.forms.review_create import ReviewForm, ReviewImageForm
from reviews.models import Review, ReviewImage
from users.models import User


class ReviewCreateView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        product = get_object_or_404(Product, id=product_id)
        
        existing_review = Review.objects.filter(
            user=cast(User, request.user),
            product=product
        ).first()

        if existing_review:
            return redirect('products-detail', product_name=product_name_to_slug(product.name))

        form = ReviewForm(request.POST)
        image_form = ReviewImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            review = form.save(commit=False)
            review.user = cast(User, request.user)
            review.product = product
            review.save()
            
            images = request.FILES.getlist('image')
            if images:
                for image in images:
                    review_image = ReviewImage.objects.create(image=image)
                    review.images.add(review_image)

            return redirect('products-detail', product_name=product_name_to_slug(product.name))

        return redirect('products-detail', product_name=product_name_to_slug(product.name))