from rest_framework import serializers
from django.utils import timezone
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'start_date', 'end_date', 'status', 'payment_id']
        read_only_fields = ['start_date', 'end_date', 'status', 'payment_id']

    def validate_plan(self, value):
        if value not in ['free', 'monthly']:
            raise serializers.ValidationError("Noto‘g‘ri plan tanlandi.")
        return value

    def create(self, validated_data):
        """Foydalanuvchi uchun yangi obuna yaratish"""
        user = self.context['request'].user

        Subscription.objects.filter(user=user, status='active').update(status='inactive')

        subscription = Subscription.objects.create(
            user=user,
            plan=validated_data['plan'],
            end_date=timezone.now() + Subscription.get_plan_duration(validated_data['plan']),
            status='active'
        )
        return subscription
