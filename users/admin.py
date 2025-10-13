from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPRequest

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'phone_number', 'is_admin', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('email', 'phone_number', 'full_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'full_name', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_admin', 'is_active')}
        ),
    )


admin.site.register(OTPRequest)
