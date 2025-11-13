import sys
import os
from pathlib import Path
from datetime import timedelta
from typing import Union
import socket

from environs import Env

import redis

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, "apps"))  # if you store apps in apps/

SECRET_KEY = env.str("SECRET_KEY", "dev-secret-key")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


DB_HOST = os.getenv("DATABASE_HOST")

UNFOLD_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
]

DJANGO_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
   
    # REST va JWT
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    # API docs
    "drf_spectacular",
    "drf_spectacular_sidecar",
    
    # Boshqa foydali app’lar
    "import_export",
    "guardian",
    "simple_history",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "silk",
]

LOCAL_APPS = [
    "users",
    "contracts",
    "subscriptions",
    'shared',
]

INSTALLED_APPS = UNFOLD_APPS + DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]


ROOT_URLCONF = env.str("ROOT_URLCONF", default="config.urls")
WSGI_APPLICATION = env.str("WSGI_APPLICATION", default="config.wsgi.application")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
try:
    socket.gethostbyname(DB_HOST)
except socket.error:
    DB_HOST = "localhost"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": DB_HOST,
        "PORT": os.getenv("DATABASE_PORT", 5432),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="uz")

LANGUAGES = (
    ("uz", _("O'zbek tili")),
    ("en", _("Ingliz tili")),
    ("ru", _("Rus tili")),
)

LOCALE_PATHS = [BASE_DIR / "locale"]

MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
MODELTRANSLATION_PREPOPULATE_LANGUAGE = LANGUAGE_CODE
MODELTRANSLATION_LANGUAGES = [language[0] for language in LANGUAGES]

TIME_ZONE = env.str("TIME_ZONE", default="Asia/Tashkent")
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = env.str("STATIC_URL", default="static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "assets"]

MEDIA_URL = env.str("MEDIA_URL", default="media/")
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

UNFOLD = {
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "LOGIN": {
        "image": lambda request: static("login-bg.png"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
    "SIDEBAR": {"show_search": True, "show_all_applications": True},
    "BORDER_RADIUS": "10px",
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

AUTH_USER_MODEL = env.str("AUTH_USER_MODEL", default="users.User")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "LEEWAY": 0,
    # Sliding tokens (if used)
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Backend docs",
    "DESCRIPTION": "Backend swagger docs (rest api service)",
    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SCHEMA_PATH_PREFIX": r"/api/",

    # Yasg dagi SECURITY_DEFINITIONS ning spectaculardagi analogi
    "COMPONENTS": {
        "securitySchemes": {
            "jwt": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Token: Bearer <access_token>",
            }
        }
    },

    # Yasgdagi SWAGGER_UI_REQUEST_HEADERS analogi
    "SECURITY": [
        {"jwt": []}
    ],
}




if not DEBUG:
    SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ("rest_framework.permissions.IsAdminUser",)
    SPECTACULAR_SETTINGS["SERVE_AUTHENTICATION"] = ("rest_framework.authentication.BasicAuthentication",)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "http://localhost:3000",
    "http://localhost:5173",
])
CORS_ALLOWED_HEADERS = [
    "content-type",
    "authorization",
    "x-requested-with",
    "accept",
    "origin",
    "accept-language",
]
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[
    "http://127.0.0.1:8000",
    "http://localhost:5173",
])


REDIS_PASSWORD = env.str("REDIS_PASSWORD", default="")
REDIS_HOST = env.str("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)

redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD or None)

REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
    }
}

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default-formatter": {
            "format": "[%(levelname)s] %(asctime)s %(filename)s:%(lineno)s:%(funcName)s: %(message)s",
            "datefmt": "%m/%d/%Y %H:%M:%S",
        },
        "request-formatter": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%m/%d/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": env.str("LOG_LEVEL", default="DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": "default-formatter",
        },
        "file": {
            "level": env.str("LOG_LEVEL", default="DEBUG"),
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "debug.log"),
            "formatter": "default-formatter",
        },
        "requests_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "requests.log"),
            "formatter": "request-formatter",
        },
    },
    "loggers": {
        "api": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "django.server": {"level": "INFO", "handlers": ["requests_file", "console"], "propagate": False},
        "": {"level": "INFO", "handlers": ["console", "file"]},
    },
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = env.int("DATA_UPLOAD_MAX_NUMBER_FIELDS", 500_000)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int("FILE_UPLOAD_MAX_MEMORY_SIZE", 20 * 1024 * 1024)  # 20 MB

EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.config.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "noreply@example.com")

PLAY_MOBILE_URL = env.str("PLAY_MOBILE_URL", default="")
PLAY_MOBILE_LOGIN = env.str("PLAY_MOBILE_LOGIN", default="")
PLAY_MOBILE_PASSWORD = env.str("PLAY_MOBILE_PASSWORD", default="")
PLAY_MOBILE_ORIGINATOR = env.str("PLAY_MOBILE_ORIGINATOR", default="")

BACKEND_URL = env.str("BACKEND_URL", default="http://localhost:8000")
FRONTEND_URL = env.str("FRONTEND_URL", default="http://localhost:5173")

SILKY_PYTHON_PROFILER = env.bool("SILKY_PYTHON_PROFILER", True)
SILKY_AUTHENTICATION = env.bool("SILKY_AUTHENTICATION", True)
SILKY_PERMISSIONS = lambda user: getattr(user, "user_role", None) == "super_admin"
SILKY_META = True
SILKY_ANALYZE_QUERIES = True

OPENAI_API_KEY = env.str("OPENAI_API_KEY", default=os.getenv("OPENAI_API_KEY", ""))
