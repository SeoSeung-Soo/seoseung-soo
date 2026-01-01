from django.urls import path

from membership.views.views import MembershipView

app_name = 'membership'

urlpatterns = [
    path('', MembershipView.as_view(), name='list'),
]