from typing import Any, Dict

from favorites.models import Favorite
from products.models import Product
from users.models import User


class FavoriteService:
    @staticmethod
    def add_to_favorites(user: User, product_id: int) -> Dict[str, Any]:
        try:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return {
                    'success': False,
                    'message': '존재하지 않는 상품입니다.',
                    'is_favorite': False
                }
            
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                product=product,
                defaults={'is_active': True}
            )
            
            if created:
                return {
                    'success': True,
                    'message': '찜하기에 추가되었습니다.',
                    'is_favorite': True
                }
            else:
                if favorite.is_active:
                    return {
                        'success': False,
                        'message': '이미 찜한 상품입니다.',
                        'is_favorite': True
                    }
                else:
                    favorite.is_active = True
                    favorite.save()
                    return {
                        'success': True,
                        'message': '찜하기에 추가되었습니다.',
                        'is_favorite': True
                    }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'오류가 발생했습니다: {str(e)}',
                'is_favorite': False
            }
    
    @staticmethod
    def remove_from_favorites(user: User, product_id: int) -> Dict[str, Any]:
        try:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return {
                    'success': False,
                    'message': '존재하지 않는 상품입니다.',
                    'is_favorite': False
                }
            
            favorite = Favorite.objects.filter(
                user=user, 
                product=product
            ).first()
            
            if favorite:
                if favorite.is_active:
                    favorite.is_active = False
                    favorite.save()
                    return {
                        'success': True,
                        'message': '찜하기에서 제거되었습니다.',
                        'is_favorite': False
                    }
                else:
                    return {
                        'success': False,
                        'message': '이미 찜하지 않은 상품입니다.',
                        'is_favorite': False
                    }
            else:
                return {
                    'success': False,
                    'message': '찜하지 않은 상품입니다.',
                    'is_favorite': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'오류가 발생했습니다: {str(e)}',
                'is_favorite': False
            }
    
    @staticmethod
    def toggle_favorite(user: User, product_id: int) -> Dict[str, Any]:
        try:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return {
                    'success': False,
                    'message': '존재하지 않는 상품입니다.',
                    'is_favorite': False
                }
            
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                product=product,
                defaults={'is_active': True}
            )
            
            if created:
                return {
                    'success': True,
                    'message': '찜하기에 추가되었습니다.',
                    'is_favorite': True
                }
            else:
                favorite.is_active = not favorite.is_active
                favorite.save()
                
                if favorite.is_active:
                    return {
                        'success': True,
                        'message': '찜하기에 추가되었습니다.',
                        'is_favorite': True
                    }
                else:
                    return {
                        'success': True,
                        'message': '찜하기에서 제거되었습니다.',
                        'is_favorite': False
                    }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'오류가 발생했습니다: {str(e)}',
                'is_favorite': False
            }
    
    @staticmethod
    def get_user_favorites(user: User) -> Any:
        return Favorite.objects.filter(user=user, is_active=True).select_related('product')
    
    @staticmethod
    def is_product_favorited(user: User, product_id: int) -> bool:
        return Favorite.objects.filter(
            user=user, 
            product_id=product_id, 
            is_active=True
        ).exists()
