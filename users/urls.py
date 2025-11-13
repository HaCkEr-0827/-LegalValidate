from django.urls import path
from .views import (
    RequestOTPView, VerifyOTPView, GoogleAuthView,
    UserRetrieveUpdateDestroyAPIView, UserListView
)

urlpatterns = [
    path('otp/request/', RequestOTPView.as_view(), name='otp_request'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp_verify'),
    path('google/', GoogleAuthView.as_view(), name='google_auth'),
    path('profile/', UserRetrieveUpdateDestroyAPIView.as_view(), name='profile'),
    path('list/', UserListView.as_view(), name='user_list'),
]
