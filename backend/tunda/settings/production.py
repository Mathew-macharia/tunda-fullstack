from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

# Production-specific overrides
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY environment variable must be set for production.")

DEBUG = False # Crucial for production!

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']: # Check for empty string after split
    raise ImproperlyConfigured("ALLOWED_HOSTS environment variable must be set for production.")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
# Ensure these are set in your VPS environment variables
if not all([DATABASES['default'].get(k) for k in ['NAME', 'USER', 'PASSWORD', 'HOST']]):
    raise ImproperlyConfigured("Production database credentials must be set as environment variables.")

STATIC_ROOT = '/var/www/gotunda/backend/staticfiles' # Your current production static root
MEDIA_ROOT = '/var/www/gotunda/backend/media' # Ensure this is correct for production

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == ['']: # Check for empty string after split
    raise ImproperlyConfigured("CORS_ALLOWED_ORIGINS environment variable must be set for production.")

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ImproperlyConfigured("GOOGLE_MAPS_API_KEY environment variable must be set for production.")

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
