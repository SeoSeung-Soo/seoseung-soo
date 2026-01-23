from django.test.client import Client

from orders.models import Order
from products.models import Product, ProductImage
from reviews.models import Review
from users.models import User


class TestSetupMixin:
    def setup_test_user_data(self) -> None:
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            role='admin',
            username='admin',
            email='admin@admin.com',
            password='admin_password',
            personal_info_consent=True,
            terms_of_use=True
        )

        self.customer_user = User.objects.create_user(
            role='customer',
            username='customer',
            email='customer@customer.com',
            password='customer',
            personal_info_consent=True,
            terms_of_use=True
        )

    def setup_test_products_data(self) -> None:
        self.image = ProductImage.objects.create(
            image='products/images/test_image.jpg',
        )

        self.product = Product.objects.create(
            user=self.admin_user,
            name='Test Product',
            description='Test Description',
            price=5.00,
            stock=5,
        )
        self.product.image.set([self.image])

    def setup_test_reviews_data(self) -> None:
        self.customer_review = Review.objects.create(
            product=self.product,
            user=self.customer_user,
            content='Customer Review Content',
            rating=4
        )
        self.admin_review = Review.objects.create(
            product=self.product,
            user=self.admin_user,
            content='Admin Review Content',
            rating=5
        )

    def setup_test_order_data(self) -> None:
        self.order = Order.objects.create(
            user=self.admin_user,
            order_id='123456',
            product_name=self.product.name,
            total_amount=50000,
            status="PAID",
            shipping_status="PENDING",
        )