from django.urls import path

from .views import OrderCreateView, OrderView
from .views.admin.order_list import AdminOrderListView
from .views.admin.shipping_management import ShippingManagementView
from .views.order_virtual_create import OrderCreateVirtualView

app_name = "orders"

urlpatterns = [
    path("status/", OrderView.as_view(), name="status"),
    path("create/", OrderCreateView.as_view(), name="create"),
    path("virtual/create/", OrderCreateVirtualView.as_view(), name="virtual-create"),
    path("admin/list/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/shipping/", ShippingManagementView.as_view(), name="admin-shipping-management"),
]
