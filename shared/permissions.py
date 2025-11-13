from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Foydalanuvchi faqat o‘z obyektini ko‘ra oladi"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminUser(BasePermission):
    """Faqat admin foydalanuvchilarga ruxsat"""
    def has_permission(self, request, view):
        return getattr(request.user, "is_admin", False)

class HasActiveSubscription(BasePermission):
    """Foydalanuvchining aktiv obunasi mavjudligini tekshirish"""
    def has_permission(self, request, view):
        user = request.user
        active_sub = getattr(user, "subscription_set", None)
        if active_sub:
            return active_sub.filter(status='active').exists()
        return False
