import os
from celery import Celery
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Set the default Django settings module for the 'celery' program.
# Determine which settings file to use
settings_module = os.environ.get('DJANGO_ENV', 'production') # Default to 'production' for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'tunda.settings.{settings_module}')

app = Celery('tunda')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
