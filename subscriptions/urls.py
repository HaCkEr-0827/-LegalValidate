from django.urls import path
from .views import (
    GetsubscriptionPlansView,
    SelectSubscriptionView,
    MySubscriptionView
)

urlpatterns = [
    path('plans/', GetsubscriptionPlansView.as_view(), name='subscription-plans'),
    path('select/', SelectSubscriptionView.as_view(), name='subscription-select'),
    path('me/', MySubscriptionView.as_view(), name='subscription-me'),
]
