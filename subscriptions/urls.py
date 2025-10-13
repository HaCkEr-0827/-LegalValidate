from django.urls import path
from .views import (
    get_my_subscription,
    select_subscription,
    get_subscription_plans
)

urlpatterns = [
    path('plans/', get_subscription_plans),
    path('select/', select_subscription),
    path('my_subscriptions/', get_my_subscription),
]
