from django.urls import path

from inquire.views.views import InquireView

urlpatterns = [
    path('', InquireView.as_view(), name='inquire'),
]