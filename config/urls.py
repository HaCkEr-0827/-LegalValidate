from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('contracts.urls')),
    path('', include('subscriptions.urls')),
]


schema_view = get_schema_view(
    openapi.Info(
        title="API hujjati",
        default_version='v1',
        description="Bu API hujjatlari Swagger orqali avtomatik generatsiya qilinadi.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]