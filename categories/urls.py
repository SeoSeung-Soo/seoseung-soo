from django.urls import path

from categories.views.category import CategoryDeleteView, CategoryView

urlpatterns = [
    path('list/', CategoryView.as_view(), name='category-list'),
    path('delete/<int:category_id>/', CategoryDeleteView.as_view(), name='category-delete'),
]