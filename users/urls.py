from django.urls import path

from users.views import LoginView
from users.views.check_duplicate import CheckDuplicateView
from users.views.consent import PersonalInfoConsent
from users.views.kakao_callback import KakaoCallbackView
from users.views.login import LogoutView
from users.views.mypage import OrderView, ProfileEditView, MyPageView
from users.views.signup import SignupView
from users.views.social_login import GoogleLoginView, NaverCallbackView, NaverLoginView

urlpatterns = [
    path("mypage/", MyPageView.as_view(), name="mypage"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("personal_info_consent/", PersonalInfoConsent.as_view(), name="personal_info_consent"),
    path("orders/", OrderView.as_view(), name="orders"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("check-duplicate/", CheckDuplicateView.as_view(), name="check-duplicate"),
    path("auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("auth/kakao/callback/", KakaoCallbackView.as_view(), name="kakao-callback"),
    path("auth/naver/", NaverLoginView.as_view(), name="naver-login"),
    path("naver/callback/", NaverCallbackView.as_view(), name="naver-callback")
]