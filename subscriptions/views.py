from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import Subscription
from .serializers import SubscriptionSerializer
from shared.utils import success_response, error_response


class GetSubscriptionPlansView(generics.GenericAPIView):
    """Tariflar ro‘yxatini olish"""
    @swagger_auto_schema(
        operation_description="Mavjud tariflar (free, monthly) ro‘yxatini olish",
        responses={200: "Tariflar ro‘yxati"}
    )
    def get(self, request, *args, **kwargs):
        plans = [
            {"plan": "free", "description": "Bepul, cheklangan funksiyalar bilan."},
            {"plan": "monthly", "description": "Oylik pullik versiya, kengaytirilgan limitlar."},
        ]
        return success_response(plans, message="Tariflar ro‘yxati")


class SelectSubscriptionView(generics.CreateAPIView):
    """Foydalanuvchi yangi obuna tanlaydi"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Yangi obuna tanlash (free yoki monthly)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['plan'],
            properties={
                'plan': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Obuna turi: free yoki monthly"
                ),
            },
        ),
        responses={201: SubscriptionSerializer()}
    )
    def post(self, request, *args, **kwargs):
        plan = request.data.get('plan')

        if plan not in ['free', 'monthly']:
            return error_response("Noto‘g‘ri plan tanlandi.", status=400)

        Subscription.objects.filter(user=request.user, status='active').update(status='inactive')

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=timezone.now() + Subscription.get_plan_duration(plan),
            status='active'
        )

        serializer = SubscriptionSerializer(subscription)
        return success_response(serializer.data, message="Yangi obuna yaratildi.", status=201)


class MySubscriptionView(generics.RetrieveAPIView):
    """Foydalanuvchining joriy aktiv obunasini olish"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchining joriy obunasini olish. Agar mavjud bo‘lmasa, free yaratiladi.",
        responses={200: SubscriptionSerializer()}
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        subscription = Subscription.objects.filter(user=user, status='active').first()

        if not subscription:
            subscription = Subscription.objects.create(
                user=user,
                plan='free',
                end_date=timezone.now() + Subscription.get_plan_duration('free'),
                status='active'
            )

        serializer = SubscriptionSerializer(subscription)
        return success_response(serializer.data, message="Joriy obuna holati.")
