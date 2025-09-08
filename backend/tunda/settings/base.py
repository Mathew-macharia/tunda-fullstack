from pathlib import Path
from datetime import timedelta
import os
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY environment variable must be set for production.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'users',
    'locations',
    'farms',
    'products',
    'carts',
    'orders',
    'payments',
    'core',
    'delivery',
    'feedback',
    'data_insights',
    'communication',
    'finance',
    
# Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'corsheaders',
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0' # Use Redis as the broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # Use Redis as the result backend
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi' # Or your desired timezone

# Configure custom user model
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tunda.urls'

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

WSGI_APPLICATION = 'tunda.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'tunda_db_copy'),
        'USER': os.environ.get('DB_USER', 'wiseman'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'nopassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Append trailing slash to URLs (set to False for API consistency with frontends)
APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = '/var/www/gotunda/backend/staticfiles' # Path where static files will be collected

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Djoser settings
DJOSER = {
    'LOGIN_FIELD': 'phone_number',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SERIALIZERS': {
        # Note: user_create serializer has issues - using /api/users/register/ instead
        'user_create': 'users.serializers.UserCreateSerializer',
        'user': 'users.serializers.UserSerializer',
        'current_user': 'users.serializers.UserSerializer',
    },
}

# SimpleJWT settings
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS settings
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')

# Africa's Talking SMS settings
AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME')
AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY')

# Allow credentials to be included in CORS requests
CORS_ALLOW_CREDENTIALS = True

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') # Must be set in production environment variables

# Caching for geocoding results and performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 86400,  # 24 hours default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 2000,
        }
    },
    'geocoding': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'geocoding-cache',
        'TIMEOUT': 86400,  # 24 hours for geocoding results
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    },
    'distance': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'distance-cache',
        'TIMEOUT': 3600,  # 1 hour for distance calculations
        'OPTIONS': {
            'MAX_ENTRIES': 500,
        }
    }
}

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = ['https://gotunda.com', 'https://www.gotunda.com']
