"""
WSGI config for tunda project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file (for local testing with WSGI server)
# In production, environment variables should be set directly by the server (e.g., Gunicorn, uWSGI)
load_dotenv()

from django.core.wsgi import get_wsgi_application

# Determine which settings file to use
settings_module = os.environ.get('DJANGO_ENV', 'production') # Default to 'production' for WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'tunda.settings.{settings_module}')

application = get_wsgi_application()
