from django.db import models

from categories.models import Category
from config.basemodel import BaseModel
from config.utils.image_path import image_upload_path
from users.models import User


def product_image_upload_path(instance: 'ProductImage', filename: str) -> str:
    return image_upload_path('products', filename)


class ProductImage(BaseModel):
    image = models.ImageField(upload_to=product_image_upload_path)
    
    class Meta:
        db_table = 'products_image'

class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True, null=True)  # 예: #ff0000 (선택적)
    class Meta:
        db_table = 'products_color'

class Product(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ManyToManyField(ProductImage, blank=True, db_table='product_image_cdt')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField()
    is_live = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, blank=True, db_table='product_category_cdt')
    colors = models.ManyToManyField(Color, blank=True, db_table='product_color_cdt')
    class Meta:
        db_table = 'products'


class WishList(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    class Meta:
        db_table = 'wish_list'