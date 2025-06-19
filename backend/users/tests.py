from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_role="customer"
        )
        self.assertEqual(user.phone_number, "0712345678")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.user_role, "customer")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            phone_number="0798765432",
            password="adminpass123",
            first_name="Admin",
            last_name="User"
        )
        self.assertEqual(admin_user.phone_number, "0798765432")
        self.assertEqual(admin_user.user_role, "admin")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_role="customer"
        )
        self.login_url = reverse('jwt-create')  # Djoser JWT URL
        
    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'phone_number': '0712345678',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)