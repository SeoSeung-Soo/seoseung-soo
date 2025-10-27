from django.db import models

from config.basemodel import BaseModel
from products.models import Product
from users.models import User


class Favorite(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'favorites'