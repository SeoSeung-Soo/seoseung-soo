from typing import Dict, Union

from django.db.models import Avg, Count

from products.models import Product
from reviews.models import Review


class ReviewCountService:
    @staticmethod
    def get_product_review_stats(product: Product) -> Dict[str, Union[float, int, Dict[int, Dict[str, Union[int, float]]]]]:
        reviews = Review.objects.filter(product=product)
        
        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )
        
        rating_distribution = {}
        for rating in range(5, 0, -1):
            count = reviews.filter(rating=rating).count()
            percentage = (count / stats['review_count'] * 100) if stats['review_count'] > 0 else 0.0
            rating_distribution[rating] = {
                'count': count,
                'percentage': round(percentage, 1)
            }
        
        return {
            'avg_rating': float(stats['avg_rating']) if stats['avg_rating'] is not None else 0.0,
            'review_count': stats['review_count'],
            'rating_distribution': rating_distribution
        }