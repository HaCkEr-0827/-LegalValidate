from django.urls import path
from .views import GetSubscriptionPlansView, SelectSubscriptionView, MySubscriptionView

urlpatterns = [
    path('plans/', GetSubscriptionPlansView.as_view(), name='subscription-plans'),
    path('select/', SelectSubscriptionView.as_view(), name='select-subscription'),
    path('me/', MySubscriptionView.as_view(), name='my-subscription'),
]
