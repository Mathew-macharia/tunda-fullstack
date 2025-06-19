"""
Pytest configuration and shared fixtures for E2E testing.
This file provides common fixtures and configuration for all E2E tests.
"""

import os
import pytest
import requests
from decimal import Decimal
from typing import Dict, Any, Optional
from django.core.management import call_command
from django.test import override_settings
from django.conf import settings
import django
from django.core.wsgi import get_wsgi_application
import time
import random

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings')
django.setup()

from users.models import User
from locations.models import Location
from farms.models import Farm
from products.models import Product, ProductCategory
from core.models import SystemSettings


class APIClient:
    """Custom API client for E2E testing with requests library"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
    
    def set_auth_token(self, token: str):
        """Set JWT authentication token"""
        self.token = token
        self.session.headers.update({'Authorization': f'JWT {token}'})
    
    def clear_auth(self):
        """Clear authentication"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to API endpoint"""
        url = f"{self.base_url}{endpoint}"
        return self.session.request(method, url, **kwargs)
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('PUT', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('PATCH', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('DELETE', endpoint, **kwargs)


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Setup test database for E2E testing"""
    with django_db_blocker.unblock():
        # Set test database name
        settings.DATABASES['default']['NAME'] = 'test_tunda_e2e'
        
        # Create test database
        call_command('migrate', verbosity=0, interactive=False)
        
        # Initialize system settings
        SystemSettings.objects.initialize_default_settings()


@pytest.fixture(scope="function")
def db_reset(django_db_setup, django_db_blocker):
    """Reset database to clean state before each test"""
    with django_db_blocker.unblock():
        # Clear all data except system settings
        User.objects.all().delete()
        Location.objects.all().delete()
        Farm.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        
        # Recreate system settings if they were deleted
        if not SystemSettings.objects.exists():
            SystemSettings.objects.initialize_default_settings()


@pytest.fixture(scope="session")
def api_base_url():
    """Get API base URL from environment or use default"""
    return os.getenv('E2E_API_BASE_URL', 'http://127.0.0.1:8000/api')


@pytest.fixture
def api_client(api_base_url):
    """Create API client instance"""
    return APIClient(api_base_url)


@pytest.fixture
def sample_user_data():
    """Sample user data for registration with unique phone numbers"""
    # Generate unique suffix for this test run
    unique_suffix = str(int(time.time()))[-6:] + str(random.randint(10, 99))
    
    return {
        'customer': {
            'phone_number': f'071234{unique_suffix}',
            'password': 'testpass123',
            're_password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Customer',
            'user_role': 'customer',
            'email': f'john.customer.{unique_suffix}@example.com'
        },
        'farmer': {
            'phone_number': f'079876{unique_suffix}',
            'password': 'farmpass123',
            're_password': 'farmpass123',
            'first_name': 'Jane',
            'last_name': 'Farmer',
            'user_role': 'farmer',
            'email': f'jane.farmer.{unique_suffix}@example.com'
        },
        'rider': {
            'phone_number': f'072345{unique_suffix}',
            'password': 'ridepass123',
            're_password': 'ridepass123',
            'first_name': 'Mike',
            'last_name': 'Rider',
            'user_role': 'rider',
            'email': f'mike.rider.{unique_suffix}@example.com'
        },
        'admin': {
            'phone_number': f'073456{unique_suffix}',
            'password': 'adminpass123',
            're_password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_role': 'admin',
            'email': f'admin.{unique_suffix}@tunda.com'
        }
    }


@pytest.fixture
def register_user():
    """Factory fixture to register users"""
    def _register_user(api_client: APIClient, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user and return registration response"""
        response = api_client.post('/users/users/', json=user_data)
        assert response.status_code == 201, f"User registration failed: {response.text}"
        return response.json()
    
    return _register_user


@pytest.fixture
def login_user():
    """Factory fixture to login users"""
    def _login_user(api_client: APIClient, phone_number: str, password: str) -> Dict[str, Any]:
        """Login user and return JWT tokens"""
        login_data = {
            'phone_number': phone_number,
            'password': password
        }
        response = api_client.post('/users/jwt/create/', json=login_data)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        tokens = response.json()
        # Set authentication token in client
        api_client.set_auth_token(tokens['access'])
        return tokens
    
    return _login_user


@pytest.fixture
def authenticated_client():
    """Factory fixture to create authenticated API clients"""
    def _authenticated_client(api_base_url: str, user_role: str, sample_user_data: Dict) -> APIClient:
        """Create authenticated API client for specific user role"""
        client = APIClient(api_base_url)
        user_data = sample_user_data[user_role]
        
        # Register user
        register_response = client.post('/users/users/', json=user_data)
        assert register_response.status_code == 201
        
        # Login user
        login_data = {
            'phone_number': user_data['phone_number'],
            'password': user_data['password']
        }
        login_response = client.post('/users/jwt/create/', json=login_data)
        assert login_response.status_code == 200
        
        # Set authentication token
        tokens = login_response.json()
        client.set_auth_token(tokens['access'])
        
        return client
    
    return _authenticated_client


@pytest.fixture
def customer_client(api_base_url, sample_user_data, authenticated_client):
    """Authenticated customer client"""
    return authenticated_client(api_base_url, 'customer', sample_user_data)


@pytest.fixture
def farmer_client(api_base_url, sample_user_data, authenticated_client):
    """Authenticated farmer client"""
    return authenticated_client(api_base_url, 'farmer', sample_user_data)


@pytest.fixture
def rider_client(api_base_url, sample_user_data, authenticated_client):
    """Authenticated rider client"""
    return authenticated_client(api_base_url, 'rider', sample_user_data)


@pytest.fixture
def admin_client(api_base_url, sample_user_data, authenticated_client):
    """Authenticated admin client"""
    return authenticated_client(api_base_url, 'admin', sample_user_data)


@pytest.fixture
def sample_location_data():
    """Sample location data"""
    return {
        'location_name': 'Nakuru Town',
        'sub_location': 'Central Business District',
        'landmark': 'Near Town Hall',
        'latitude': -0.2833,
        'longitude': 36.0699,
        'is_default': True
    }


@pytest.fixture
def sample_farm_data():
    """Sample farm data"""
    return {
        'farm_name': 'Green Valley Farm',
        'total_acreage': 5.5,
        'farm_description': 'Organic vegetable farm in the highlands',
        'is_certified_organic': True,
        'weather_zone': 'highland'
    }


@pytest.fixture
def sample_product_category_data():
    """Sample product category data"""
    return {
        'category_name': 'Vegetables',
        'description': 'Fresh vegetables and leafy greens',
        'is_active': True
    }


@pytest.fixture
def sample_product_data():
    """Sample product data"""
    return {
        'product_name': 'Tomatoes',
        'description': 'Fresh red tomatoes',
        'unit_of_measure': 'kg',
        'is_perishable': True,
        'shelf_life_days': 7,
        'is_active': True
    }


@pytest.fixture
def create_test_data():
    """Factory to create complete test data setup"""
    def _create_test_data(farmer_client: APIClient, admin_client: APIClient, 
                         sample_location_data: Dict, sample_farm_data: Dict,
                         sample_product_category_data: Dict, sample_product_data: Dict):
        """Create complete test data setup with location, farm, category, and product"""
        
        # Create location for farmer
        location_response = farmer_client.post('/locations/', json=sample_location_data)
        assert location_response.status_code == 201
        location = location_response.json()
        
        # Create farm
        farm_data = {**sample_farm_data, 'location': location['location_id']}
        farm_response = farmer_client.post('/farms/', json=farm_data)
        assert farm_response.status_code == 201
        farm = farm_response.json()
        
        # Create product category (admin only) - handle existing categories
        category_response = admin_client.post('/products/categories/', json=sample_product_category_data)
        if category_response.status_code == 400 and 'already exists' in category_response.text:
            # Category already exists, fetch it instead
            categories_response = admin_client.get('/products/categories/')
            assert categories_response.status_code == 200
            categories = categories_response.json()
            category = None
            for cat in categories:
                if cat['category_name'] == sample_product_category_data['category_name']:
                    category = cat
                    break
            assert category is not None, "Could not find or create category"
        else:
            assert category_response.status_code == 201
            category = category_response.json()
        
        # Create product
        product_data = {**sample_product_data, 'category': category['category_id']}
        product_response = farmer_client.post('/products/items/', json=product_data)
        assert product_response.status_code == 201
        product = product_response.json()
        
        return {
            'location': location,
            'farm': farm,
            'category': category,
            'product': product
        }
    
    return _create_test_data


@pytest.fixture
def sample_product_listing_data():
    """Sample product listing data"""
    return {
        'current_price': 150.00,
        'quantity_available': 50.0,
        'min_order_quantity': 1.0,
        'harvest_date': '2024-01-15',
        'quality_grade': 'premium',
        'is_organic_certified': True,
        'listing_status': 'available',
        'notes': 'Fresh organic tomatoes harvested this morning'
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            **{
                'USE_TZ': True,
                'DATABASES': {
                    'default': {
                        'ENGINE': 'django.db.backends.mysql',
                        'NAME': 'test_tunda_e2e',
                        'USER': 'wiseman',
                        'PASSWORD': 'nopassword',
                        'HOST': 'localhost',
                        'PORT': '3306',
                        'OPTIONS': {
                            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
                        }
                    }
                }
            }
        )
        django.setup() 