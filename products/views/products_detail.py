from django.db.models import Prefetch
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

from favorites.services.favorite_service import FavoriteService
from products.models import Product
from reviews.forms.review_create import ReviewCommentForm, ReviewForm, ReviewImageForm
from reviews.models import Review, ReviewComment
from reviews.services.review_count import ReviewCountService


class ProductsDetailView(View):
    def get(self, request: HttpRequest, product_name: str) -> HttpResponse:
        products = get_object_or_404(Product.objects.prefetch_related('colors'), name=product_name)
        
        reviews = Review.objects.filter(
            product=products,
            is_published=True
        ).select_related('user').prefetch_related(
            'images', 
            Prefetch('comments', queryset=ReviewComment.objects.all().select_related('user'))
        ).order_by('-created_at')
        
        review_stats = ReviewCountService.get_product_review_stats(products)
        
        user_review = None
        if request.user.is_authenticated:
            user_review = next((review for review in reviews if review.user == request.user), None)
        
        is_favorited = False
        if request.user.is_authenticated:
            is_favorited = FavoriteService.is_product_favorited(request.user, products.id)
        
        review_form = ReviewForm()
        review_image_form = ReviewImageForm()
        
        comment_form = ReviewCommentForm()
        
        context = {
            "products": products,
            "reviews": reviews,
            "avg_rating": review_stats['avg_rating'],
            "review_count": review_stats['review_count'],
            "photo_review_count": review_stats['photo_review_count'],
            "rating_distribution": review_stats['rating_distribution'],
            "user_review": user_review,
            "is_favorited": is_favorited,
            "review_form": review_form,
            "review_image_form": review_image_form,
            "comment_form": comment_form,
        }
        return render(request, "products/detail.html", context)