from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import SystemSettings
from users.models import User
import json

class SystemSettingsModelTestCase(TestCase):
    """Test case for the SystemSettings model"""
    
    def setUp(self):
        # Create test settings
        self.string_setting = SystemSettings.objects.create(
            setting_key="test_string",
            setting_value="test value",
            setting_type="string",
            description="Test string setting"
        )
        
        self.number_setting = SystemSettings.objects.create(
            setting_key="test_number",
            setting_value="123.45",
            setting_type="number",
            description="Test number setting"
        )
        
        self.boolean_setting = SystemSettings.objects.create(
            setting_key="test_boolean",
            setting_value="true",
            setting_type="boolean",
            description="Test boolean setting"
        )
        
        self.json_setting = SystemSettings.objects.create(
            setting_key="test_json",
            setting_value='{"key": "value"}',
            setting_type="json",
            description="Test JSON setting"
        )
    
    def test_get_setting_string(self):
        """Test getting a string setting"""
        value = SystemSettings.objects.get_setting("test_string")
        self.assertEqual(value, "test value")
        self.assertIsInstance(value, str)
    
    def test_get_setting_number(self):
        """Test getting a number setting"""
        from decimal import Decimal
        value = SystemSettings.objects.get_setting("test_number")
        self.assertEqual(value, Decimal('123.45'))
        self.assertIsInstance(value, Decimal)
    
    def test_get_setting_boolean(self):
        """Test getting a boolean setting"""
        value = SystemSettings.objects.get_setting("test_boolean")
        self.assertEqual(value, True)
        self.assertIsInstance(value, bool)
    
    def test_get_setting_json(self):
        """Test getting a JSON setting"""
        value = SystemSettings.objects.get_setting("test_json")
        self.assertEqual(value, {"key": "value"})
        self.assertIsInstance(value, dict)
    
    def test_get_setting_default(self):
        """Test getting a non-existent setting with a default value"""
        value = SystemSettings.objects.get_setting("non_existent", default="default")
        self.assertEqual(value, "default")

class SystemSettingsAPITestCase(APITestCase):
    """Test case for the SystemSettings API"""
    
    def setUp(self):
        # Create admin and regular users
        self.admin_user = User.objects.create_user(
            phone_number="+1234567890",
            email="admin@test.com",
            password="testpassword",
            first_name="Admin",
            last_name="User",
            user_role="admin"
        )
        
        self.customer_user = User.objects.create_user(
            phone_number="+0987654321",
            email="customer@test.com",
            password="testpassword",
            first_name="Customer",
            last_name="User",
            user_role="customer"
        )
        
        # Create test settings
        self.delivery_fee = SystemSettings.objects.create(
            setting_key="delivery_fee_per_km",
            setting_value="50",
            setting_type="number",
            description="Delivery fee in KES per kilometer"
        )
        
        self.min_order = SystemSettings.objects.create(
            setting_key="min_order_amount",
            setting_value="500",
            setting_type="number",
            description="Minimum order amount in KES"
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_list_settings_as_admin(self):
        """Test that admin users can list all settings"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('settings-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_settings_as_customer(self):
        """Test that non-admin users cannot list all settings"""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(reverse('settings-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_public_settings(self):
        """Test getting public settings as a customer"""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(reverse('settings-public'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Both of our test settings should be public
        self.assertEqual(len(response.data), 2)
    
    def test_get_setting_by_key(self):
        """Test getting a setting by key as a customer"""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f"{reverse('settings-by-key')}?key=delivery_fee_per_km")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['key'], 'delivery_fee_per_km')
        self.assertEqual(response.data['value'], 50)
    
    def test_create_setting_as_admin(self):
        """Test that admin users can create settings"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'setting_key': 'new_setting',
            'setting_value': 'new value',
            'setting_type': 'string',
            'description': 'New test setting'
        }
        response = self.client.post(reverse('settings-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SystemSettings.objects.count(), 3)
    
    def test_create_setting_as_customer(self):
        """Test that non-admin users cannot create settings"""
        self.client.force_authenticate(user=self.customer_user)
        data = {
            'setting_key': 'new_setting',
            'setting_value': 'new value',
            'setting_type': 'string',
            'description': 'New test setting'
        }
        response = self.client.post(reverse('settings-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(SystemSettings.objects.count(), 2)
