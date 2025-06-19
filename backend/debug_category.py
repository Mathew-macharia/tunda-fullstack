import requests
import sys
import os
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings')
import django
django.setup()
from tests.conftest import APIClient

# Test admin user creation and category creation
api_client = APIClient('http://127.0.0.1:8000/api')

# Test admin user data
admin_data = {
    'phone_number': '0734567891',
    'password': 'adminpass123',
    're_password': 'adminpass123', 
    'first_name': 'Admin',
    'last_name': 'User',
    'user_role': 'admin',
    'email': 'admin2@tunda.com'
}

print('1. Registering admin user...')
reg_response = api_client.post('/users/users/', json=admin_data)
print(f'   Registration status: {reg_response.status_code}')
if reg_response.status_code != 201:
    print(f'   Error: {reg_response.text}')
    sys.exit(1)

print('2. Logging in admin user...')
login_response = api_client.post('/users/jwt/create/', json={
    'phone_number': admin_data['phone_number'],
    'password': admin_data['password']
})
print(f'   Login status: {login_response.status_code}')
if login_response.status_code != 200:
    print(f'   Error: {login_response.text}')
    sys.exit(1)

tokens = login_response.json()
api_client.set_auth_token(tokens['access'])

print('3. Checking existing categories...')
categories_response = api_client.get('/products/categories/')
print(f'   Categories status: {categories_response.status_code}')
print(f'   Categories response: {categories_response.text}')
categories = categories_response.json()
print(f'   Categories type: {type(categories)}')
print(f'   Categories keys: {categories.keys() if isinstance(categories, dict) else "Not a dict"}')

print('4. Creating product category...')
category_data = {
    'category_name': 'Vegetables',
    'description': 'Fresh vegetables and leafy greens',
    'is_active': True
}
cat_response = api_client.post('/products/categories/', json=category_data)
print(f'   Category creation status: {cat_response.status_code}')
print(f'   Response: {cat_response.text}') 