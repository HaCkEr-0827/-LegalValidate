from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import Subscription
from .serializers import SubscriptionSerializer

class GetsubscriptionPlansView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_description="Mavjud tariflar ro‘yxatini olish",
        responses={200: "Tariflar ro‘yxati"},
    )
    def get(self, request, *args, **kwargs):
        plans = [
            {"plan": "free", "description": "Bepul, cheklangan funksiyalar"},
            {"plan": "monthly", "description": "Oylik pullik versiya, kengaytirilgan limitlar"},
        ]
        return Response(plans)

class SelectSubscriptionView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi yangi obuna tanlaydi (free yoki monthly)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['plan'],
            properties={
                'plan': openapi.Schema(type=openapi.TYPE_STRING, description="free yoki monthly"),
            },
        ),
        responses={201: SubscriptionSerializer()}
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        plan = request.data.get('plan')

        if plan not in ['free', 'monthly']:
            return Response({"error": "Noto‘g‘ri plan tanlandi."}, status=400)

        Subscription.objects.filter(user=user, status='active').update(status='inactive')

        sub = Subscription.objects.create(
            user=user,
            plan=plan,
            end_date=timezone.now() + Subscription.get_plan_duration(plan),
            status='active'
        )

        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data, status=201)

class MySubscriptionView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchining joriy aktiv obunasini olish (agar yo‘q bo‘lsa free yaratiladi)",
        responses={200: SubscriptionSerializer()}
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        sub = Subscription.objects.filter(user=user, status='active').first()

        if not sub:
            sub = Subscription.objects.create(
                user=user,
                plan='free',
                end_date=timezone.now() + Subscription.get_plan_duration('free'),
                status='active'
            )

        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data)