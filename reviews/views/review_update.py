import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from products.utils.url_slug import product_name_to_slug
from reviews.forms.review_create import ReviewForm, ReviewImageForm
from reviews.models import Review, ReviewImage


class ReviewUpdateView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def get(self, request: HttpRequest, review_id: int) -> HttpResponse:
        review = get_object_or_404(Review, id=review_id)

        # 본인의 리뷰인지 확인
        if review.user != request.user:
            raise Http404("권한이 없습니다.")

        form = ReviewForm(instance=review)
        image_form = ReviewImageForm()

        context = {
            'form': form,
            'image_form': image_form,
            'review': review,
            'product': review.product
        }
        return render(request, 'reviews/review_update.html', context)

    def post(self, request: HttpRequest, review_id: int) -> HttpResponse:
        review = get_object_or_404(Review, id=review_id)

        # 본인의 리뷰인지 확인
        if review.user != request.user:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': '권한이 없습니다.'
                }, status=403)
            raise Http404("권한이 없습니다.")

        # AJAX 요청 처리
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                form = ReviewForm(data, instance=review)

                if form.is_valid():
                    updated_review = form.save()
                    
                    return JsonResponse({
                        'success': True,
                        'review': {
                            'id': updated_review.id,
                            'content': updated_review.content,
                            'rating': updated_review.rating,
                            'star_display': updated_review.get_star_display(),
                            'created_at': updated_review.created_at.strftime('%Y.%m.%d')
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '입력 내용을 확인해주세요.',
                        'errors': form.errors
                    }, status=400)
            
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': '잘못된 요청입니다.'
                }, status=400)

        # 일반 POST 요청 처리 (파일 업로드 등)
        form = ReviewForm(request.POST, instance=review)
        image_form = ReviewImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            form.save()

            # 새 이미지 추가
            images = request.FILES.getlist('image')
            if images:
                for image in images:
                    review_image = ReviewImage.objects.create(image=image)
                    review.images.add(review_image)

            return redirect('products-detail', product_name=product_name_to_slug(review.product.name))

        context = {
            'form': form,
            'image_form': image_form,
            'review': review,
            'product': review.product
        }
        return render(request, 'reviews/review_update.html', context)