"""
Django settings for project project.
"""

from pathlib import Path
from datetime import timedelta
import os

# ======================================================
# BASE DIR
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# SECURITY
# ======================================================
SECRET_KEY = 'django-insecure-3emgqr#1%ih0ay7swkiuv1qk#scwf$=irv0du*kht236(edy^f'
DEBUG = True
ALLOWED_HOSTS = []


# ======================================================
# APPLICATIONS
# ======================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_extensions',

    'core',
]


# ======================================================
# DJANGO REST FRAMEWORK
# ======================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}


# ======================================================
# SIMPLE JWT CONFIGURATION
# ======================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ======================================================
# DRF SPECTACULAR (SWAGGER)
# ======================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "ngrPharma API",
    "DESCRIPTION": "Backend ngrPharma – gestion pharmacies",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"BearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}


# ======================================================
# MIDDLEWARE
# ======================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
]


# ======================================================
# URL / WSGI
# ======================================================
ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'


# ======================================================
# TEMPLATES
# ======================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================================================
# DATABASE — PostgreSQL
# ======================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ngrpharma',
        'USER': 'postgres',
        'PASSWORD': '@1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ======================================================
# PASSWORD VALIDATION
# ======================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ======================================================
# INTERNATIONALIZATION
# ======================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ======================================================
# STATIC FILES
# ======================================================
STATIC_URL = 'static/'


# ======================================================
# DEFAULT PRIMARY KEY
# ======================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================
# CUSTOM USER MODEL
# ======================================================
AUTH_USER_MODEL = "core.CustomUser"

# ==========================================
# CORS SETTINGS
# ==========================================
CORS_ALLOW_ALL_ORIGINS = True

# (option plus propre en prod)
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
# ]

# ===============================
# STRIPE CONFIG
# ===============================

# ===============================
# STRIPE CONFIG (SECURE)
# ===============================
from dotenv import load_dotenv
load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

STRIPE_SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL",
    "http://localhost:3000/billing/success"
)

STRIPE_CANCEL_URL = os.getenv(
    "STRIPE_CANCEL_URL",
    "http://localhost:3000/billing/cancel"
)