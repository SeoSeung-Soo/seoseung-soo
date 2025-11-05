from django.urls import path

from .views import OrderCreateView, OrderView

app_name = "orders"

urlpatterns = [
    path("status/", OrderView.as_view(), name="status"),
    path("create/", OrderCreateView.as_view(), name="create"),
]
