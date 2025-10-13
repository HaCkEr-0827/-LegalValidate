from django.db import models
from django.utils import timezone
from datetime import timedelta
from users.models import User


class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email or self.user.phone_number} - {self.plan}"

    @staticmethod
    def get_plan_duration(plan):
        if plan == 'monthly':
            return timedelta(days=30)
        return timedelta(days=9999)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + self.get_plan_duration(self.plan)
        super().save(*args, **kwargs)
