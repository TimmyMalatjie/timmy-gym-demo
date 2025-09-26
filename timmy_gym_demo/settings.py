"""
Django settings for timmy_gym_demo project.
"""

from pathlib import Path
import os
from decouple import config # Used to read .env/environment variables
import dj_database_url # Used to parse DATABASE_URL (recommended for production)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. CORE ENVIRONMENT CONFIGURATION (Must read from environment/decouple only)
# ==============================================================================

# **CRITICAL FIX 1: Use environment variables, not hardcoded defaults.**
# Ensure SECRET_KEY is loaded from environment; fallback to hardcoded value ONLY for local dev.
SECRET_KEY = config('SECRET_KEY', default='django-insecure-yqr=^ombi!^#^8#b9u%ssjsb-28f&h!2o3yaty1@b2x_fqkn1a')

# DEBUG is loaded from environment and cast to a boolean. Default should be True for local dev.
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS is loaded from environment as a comma-separated string, then split.
# Fallback to a single host for local development.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# ==============================================================================
# 2. APPLICATION DEFINITION
# ==============================================================================

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
    'whitenoise.runserver_nostatic', # For development/WhiteNoise
    
    # Cloud/Storage
    'storages',
    
    # Local apps
    'core',
    'accounts',
    'memberships',
    'bookings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # **CRITICAL FIX 2: Add WhiteNoise middleware for serving static files in production.**
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
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'timmy_gym_demo.wsgi.application'

# ==============================================================================
# 3. DATABASE
# ==============================================================================

# **CRITICAL FIX 3: Use dj_database_url for robust production database handling.**
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        cast=dj_database_url.parse
    )
}

# ... (Password validation settings skipped for brevity)

# ==============================================================================
# 4. STATIC AND MEDIA FILES (Production-Ready Configuration)
# ==============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Static files are collected into this directory
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# **CRITICAL FIX 4: WhiteNoise for static files in production.**
# This tells Django to use the WhiteNoise storage backend for optimized serving.
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    # Set default storage to S3 for user media (see below)
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Media files (User Uploads) - S3 Configuration
# Use S3 for user-uploaded media ONLY when DEBUG is False (i.e., production)
if not DEBUG:
    # Read S3 credentials from environment variables
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default=None)
    
    if AWS_STORAGE_BUCKET_NAME:
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


# ... (I18n, Auth, Crispy settings skipped for brevity as they are fine)

# ==============================================================================
# 5. FINAL CHECKS
# ==============================================================================

# Define a secure redirect scheme when DEBUG is False
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
# Django's default log configuration is sufficient unless you need complex setup
# The DEBUG log setup is only included if DEBUG is True (local development).
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.template': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'