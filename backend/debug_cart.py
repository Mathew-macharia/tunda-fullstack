import requests
import sys
import os
import json
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings')
import django
django.setup()
from tests.conftest import APIClient

# Test the orders endpoint
api_client = APIClient('http://127.0.0.1:8000/api')

# Use sample test data
customer_data = {
    'phone_number': '0712349999',
    'password': 'testpass123',
    're_password': 'testpass123', 
    'first_name': 'Debug',
    'last_name': 'Customer',
    'user_role': 'customer',
    'email': 'debug.customer@example.com'
}

print("1. Creating customer...")
try:
    register_response = api_client.post('/users/register/', json=customer_data)
    print(f"Customer creation: {register_response.status_code}")
    if register_response.status_code == 201:
        print("Customer created successfully")
    
    # Login the customer
    login_response = api_client.post('/users/login/', json={
        'phone_number': customer_data['phone_number'],
        'password': customer_data['password']
    })
    print(f"Customer login: {login_response.status_code}")
    
    if login_response.status_code == 200:
        customer_token = login_response.json()['access']
        api_client.set_token(customer_token)
        print("Customer authenticated")
        
        # Test orders endpoint - first just a GET
        print("\n2. Testing orders GET endpoint...")
        orders_get_response = api_client.get('/orders/')
        print(f"GET /orders/ status: {orders_get_response.status_code}")
        print(f"GET /orders/ response: {orders_get_response.json()}")
        
        # Test orders endpoint - POST with minimal data
        print("\n3. Testing orders POST endpoint...")
        orders_post_response = api_client.post('/orders/', json={'test': 'data'})
        print(f"POST /orders/ status: {orders_post_response.status_code}")
        print(f"POST /orders/ response: {orders_post_response.json()}")
        
    else:
        print(f"Customer login failed: {login_response.json()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 