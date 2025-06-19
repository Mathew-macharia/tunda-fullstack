import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, '.')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings')

# Setup Django
django.setup()

# Now we can import Django models and make requests
from django.contrib.auth import get_user_model
from django.test import Client
import json

User = get_user_model()

# Create a test user
user_data = {
    'phone_number': '0712349999',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'Customer',
    'user_role': 'customer',
    'email': 'test@example.com'
}

# Use Django test client for a more direct test
client = Client()

# Check if user exists, if not create one
try:
    user = User.objects.get(phone_number=user_data['phone_number'])
    print(f"User already exists: {user}")
except User.DoesNotExist:
    user = User.objects.create_user(**user_data)
    print(f"Created user: {user}")

# Test direct access to orders view
from orders.views import OrderViewSet
from rest_framework.test import APIRequestFactory, force_authenticate

factory = APIRequestFactory()

# Create a POST request to simulate order creation
request = factory.post('/orders/', {}, format='json')
force_authenticate(request, user=user)
request.user = user  # Explicitly set the user

# Try to instantiate the viewset
viewset = OrderViewSet()
viewset.request = request
viewset.format_kwarg = None
viewset.action = 'create'  # Set the action to simulate create operation

print(f"User role: {user.user_role}")
print(f"User authenticated: {user.is_authenticated}")
print(f"Queryset: {viewset.get_queryset()}")
print(f"Serializer class: {viewset.get_serializer_class()}")
print(f"Allowed methods: {viewset.allowed_methods}")
print(f"HTTP method names: {getattr(viewset, 'http_method_names', 'Not set')}")

# Test permissions directly
from orders.views import IsCustomer
permission = IsCustomer()
print(f"Permission has_permission: {permission.has_permission(request, viewset)}")

# Try to call the allowed_methods directly
try:
    print(f"Actions: {viewset.get_view_name()}")
except Exception as e:
    print(f"Error getting view name: {e}")

# Check what methods are allowed for this specific request
print(f"Request method: {request.method}")
print(f"Request user: {request.user}")
print(f"Request user role: {request.user.user_role}")
print(f"Request user authenticated: {request.user.is_authenticated}") 