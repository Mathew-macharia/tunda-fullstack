from .base import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Override base settings for local development
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-insecure-local-secret-key') # Provide a default for local
DEBUG = True
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') # Read from .env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'tunda_local_db'), # Local DB name
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5174,http://127.0.0.1:5174').split(',') # Read from .env

# Other local-specific settings (e.g., email backend for console, local file storage)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_local') # Local static files
