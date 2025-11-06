from django.urls import path

from .views import OrderCreateView, OrderView
from .views.order_virtual_create import OrderCreateVirtualView

app_name = "orders"

urlpatterns = [
    path("status/", OrderView.as_view(), name="status"),
    path("create/", OrderCreateView.as_view(), name="create"),
    path("virtual/create/", OrderCreateVirtualView.as_view(), name="virtual-create")
]
