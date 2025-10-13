# from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import Subscription
from .serializers import SubscriptionSerializer

# class UserSubscriptionListCreateView(generics.ListCreateAPIView):
#     serializer_class = SubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Swagger dokumentatsiyasi uchun fake view tekshiruvi
#         if getattr(self, 'swagger_fake_view', False):
#             return Subscription.objects.none()
#         return Subscription.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class UserSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = SubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         if getattr(self, 'swagger_fake_view', False):
#             return Subscription.objects.none()
#         return Subscription.objects.filter(user=self.request.user)




@swagger_auto_schema(
    method='get',
    operation_description="Mavjud tariflar ro‘yxatini olish",
    responses={200: "Tariflar ro‘yxati"},
)
@api_view(['GET'])
def get_subscription_plans(request):
    plans = [
        {"plan": "free", "description": "Bepul, cheklangan funksiyalar"},
        {"plan": "monthly", "description": "Oylik pullik versiya, kengaytirilgan limitlar"},
    ]
    return Response(plans)


@swagger_auto_schema(
    method='post',
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_subscription(request):
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


@swagger_auto_schema(
    method='get',
    operation_description="Foydalanuvchining joriy aktiv obunasini olish (agar yo‘q bo‘lsa free yaratiladi)",
    responses={200: SubscriptionSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_subscription(request):
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