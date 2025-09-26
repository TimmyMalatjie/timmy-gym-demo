"""
Django settings for timmy_gym_demo project.
"""

from pathlib import Path
import os
from decouple import config # Used to read .env/environment variables
import dj_database_url # Used to parse DATABASE_URL

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. CORE ENVIRONMENT CONFIGURATION
# ==============================================================================

# CRITICAL FIX 1: Removed duplicate, hardcoded SECRET_KEY, DEBUG, and ALLOWED_HOSTS definitions.
# Load values from environment/decouple.

# SECRET_KEY is loaded from environment; fallback is the insecure key (for local dev ONLY).
SECRET_KEY = config('SECRET_KEY', default='django-insecure-yqr=^ombi!^#^8#b9u%ssjsb-28f&h!2o3yaty1@b2x_fqkn1a')

# DEBUG is loaded from environment and cast to a boolean.
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,timmy-gym-demo-production.up.railway.app'
).split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party packages
    'crispy_forms',
    'crispy_bootstrap5',
    
    # WhiteNoise is added to INSTALLED_APPS for management command override, but the middleware is key.
    'whitenoise.runserver_nostatic',
    'storages',
    
    # Local apps
    'core',
    'accounts',
    'memberships',
    'bookings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CRITICAL FIX 2: WhiteNoise middleware placement for serving static files in production.
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'timmy_gym_demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates', 
            BASE_DIR / 'timmy_gym_demo' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG, # Uses the environment-controlled DEBUG variable
        },
    },
]

WSGI_APPLICATION = 'timmy_gym_demo.wsgi.application'

# ==============================================================================
# 2. DATABASE CONFIGURATION
# ==============================================================================

# CRITICAL FIX 3: Use dj_database_url to parse the production DATABASE_URL.
DATABASES = {
    'default': config(
        'DATABASE_URL',
        # Fallback to local SQLite for development
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        cast=dj_database_url.parse
    )
}

# ... (Password validation settings skipped for brevity)

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg' 
USE_I18N = True
USE_TZ = True

# ==============================================================================
# 3. STATIC AND MEDIA FILES (Production-Ready)
# ==============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Static files are collected into this directory
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# CRITICAL FIX 4: WhiteNoise storage for efficient production static serving.
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    # Default storage set to FileSystemStorage (local) initially.
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Media files (User Uploads) - S3 Configuration
# User S3 for media storage ONLY when DEBUG is False (i.e., production)
if not DEBUG:
    # Read S3 credentials from environment variables (mandatory for deployment)
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default=None)
    
    if AWS_STORAGE_BUCKET_NAME:
        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
        AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
        AWS_QUERYSTRING_AUTH = config('AWS_QUERYSTRING_AUTH', default=False, cast=bool)
        
        # Override default storage to use S3
        STORAGES['default']['BACKEND'] = 'storages.backends.s3.S3Storage'
        
        # Set Media URL to S3 bucket
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
        MEDIA_ROOT = '' # Not needed when using S3

else:
    # Development media settings (local disk)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# Bootstrap 5 Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# FINAL PRODUCTION SECURITY CHECKS
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    # Necessary for reverse proxies like Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
