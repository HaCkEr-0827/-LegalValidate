import os
import docx # type: ignore
import requests
from PyPDF2 import PdfReader # type: ignore
from rest_framework import serializers, status, permissions, parsers, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore
from shared.utils import generate_otp_code
from shared.utils import success_response, error_response
from .models import OTPRequest, User
from shared.tasks import send_otp_via_console, send_otp_via_email
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, UserSerializer


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Foydalanuvchi profilini ko‘rish (GET), tahrirlash (PUT/PATCH), va o‘chirish (DELETE)
    uchun CRUD view.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Har doim faqat o‘z profilini ko‘rsatadi
        return self.request.user

    @swagger_auto_schema(
        operation_description="Foydalanuvchi profilini olish",
        responses={200: UserSerializer()}
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Foydalanuvchi profilini yangilash",
        request_body=UserSerializer,
        responses={200: UserSerializer()}
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Foydalanuvchi profilini o‘chirish",
        responses={204: 'Profil o‘chirildi'}
    )
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({'detail': 'Profil o‘chirildi'}, status=status.HTTP_204_NO_CONTENT)

class RequestOTPView(generics.CreateAPIView):
    serializer_class = RequestOTPSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Email yoki telefon orqali OTP so‘rash",
        request_body=RequestOTPSerializer,
        responses={
            200: openapi.Response(description="OTP yuborildi"),
            400: openapi.Response(description="Email yoki telefon kiritilishi kerak")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone_number')
        code = generate_otp_code()
        OTPRequest.objects.create(email=email, phone_number=phone, code=code)

        if email:
            send_otp_via_email.delay(email, code)
        else:
            send_otp_via_console.delay(phone, code)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
 
class VerifyOTPView(generics.CreateAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="OTP tekshirish va JWT olish",
        request_body=VerifyOTPSerializer,
        responses={
            200: openapi.Response(description="JWT token qaytarildi"),
            400: openapi.Response(description="Noto‘g‘ri yoki muddati o‘tgan OTP")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone_number')
        code = serializer.validated_data.get('otp')

        otp_qs = OTPRequest.objects.filter(code=code, is_used=False)
        if email:
            otp_qs = otp_qs.filter(email=email)
        if phone:
            otp_qs = otp_qs.filter(phone_number=phone)

        otp_obj = otp_qs.order_by('-created_at').first()
        if not otp_obj or not otp_obj.is_valid():
            return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_used = True
        otp_obj.save()

        if email:
            user, created = User.objects.get_or_create(email=email, defaults={"is_active": True})
        else:
            user, created = User.objects.get_or_create(phone_number=phone, defaults={"is_active": True})

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_200_OK)

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True, help_text="Google id_token")

class GoogleAuthView(generics.CreateAPIView):
    serializer_class = GoogleAuthSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Google OAuth2 orqali login qilish",
        request_body=GoogleAuthSerializer,
        responses={
            200: openapi.Response(description="JWT token qaytarildi"),
            400: openapi.Response(description="Id_token kerak yoki noto‘g‘ri token")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_token = serializer.validated_data['id_token']

        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        r = requests.get(google_verify_url)
        if r.status_code != 200:
            return Response({"detail": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
        data = r.json()
        google_sub = data.get('sub')
        email = data.get('email')

        if not google_sub:
            return Response({"detail": "Google token missing sub"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            google_sub_id=google_sub,
            defaults={"email": email, "is_active": True}
        )
        if created and email:
            user.email = email
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Barcha foydalanuvchilar ro‘yxatini olish (faqat adminlar uchun)",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        if not getattr(request.user, 'is_admin', False):
            return Response({"detail": "Sizda bu amalni bajarish huquqi yo‘q."}, status=status.HTTP_403_FORBIDDEN)
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
