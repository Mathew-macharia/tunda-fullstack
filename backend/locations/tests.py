from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Location

User = get_user_model()

class LocationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_role="customer"
        )
        
    def test_create_location(self):
        location = Location.objects.create(
            user=self.user,
            location_name="Nakuru Town",
            sub_location="Central Business District",
            landmark="Near Town Hall",
            longitude=36.0699,  # Approximate coordinates for Nakuru
            latitude=-0.2833,
            is_default=True
        )
        
        self.assertEqual(location.location_name, "Nakuru Town")
        self.assertEqual(location.user, self.user)
        self.assertTrue(location.is_default)
        self.assertEqual(float(location.longitude), 36.0699)  # Decimal to float conversion
        self.assertEqual(float(location.latitude), -0.2833)
        
    def test_default_location_behavior(self):
        # Create a default location
        location1 = Location.objects.create(
            user=self.user,
            location_name="Home",
            longitude=36.0699,
            latitude=-0.2833,
            is_default=True
        )
        
        # Create another default location
        location2 = Location.objects.create(
            user=self.user,
            location_name="Work",
            longitude=36.0700,
            latitude=-0.2834,
            is_default=True
        )
        
        # Refresh location1 from database
        location1.refresh_from_db()
        
        # First location should no longer be default
        self.assertFalse(location1.is_default)
        self.assertTrue(location2.is_default)

class LocationAPITests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_role="customer"
        )
        
        self.user2 = User.objects.create_user(
            phone_number="0787654321",
            password="testpass456",
            first_name="Another",
            last_name="User",
            user_role="customer"
        )
        
        # Create test locations
        self.location1 = Location.objects.create(
            user=self.user1,
            location_name="Home",
            sub_location="Residential Area",
            landmark="Blue Gate",
            longitude=36.0699,
            latitude=-0.2833,
            is_default=True
        )
        
        self.location2 = Location.objects.create(
            user=self.user2,
            location_name="Farm",
            sub_location="Njoro",
            landmark="Near River",
            longitude=36.1000,
            latitude=-0.3000,
            is_default=True
        )
        
        self.client = APIClient()
        
    def test_list_user_locations(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Get list of locations
        url = reverse('location-list')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location_name'], 'Home')
        
    def test_create_location(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Create new location
        url = reverse('location-list')
        data = {
            'location_name': 'Work',
            'sub_location': 'Industrial Area',
            'landmark': 'Near Factory',
            'latitude': -0.2900,
            'longitude': 36.0800,
            'is_default': False
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.filter(user=self.user1).count(), 2)
        
    def test_retrieve_location(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Get location details
        url = reverse('location-detail', args=[self.location1.location_id])
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location_name'], 'Home')
        self.assertEqual(float(response.data['latitude']), -0.2833)
        self.assertEqual(float(response.data['longitude']), 36.0699)
        
    def test_update_location(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Update location
        url = reverse('location-detail', args=[self.location1.location_id])
        data = {
            'location_name': 'Updated Home',
            'landmark': 'New Landmark',
            'latitude': -0.2833,
            'longitude': 36.0699
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location_name'], 'Updated Home')
        self.assertEqual(response.data['landmark'], 'New Landmark')
        
    def test_delete_location(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Delete location
        url = reverse('location-detail', args=[self.location1.location_id])
        response = self.client.delete(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Location.objects.filter(user=self.user1).count(), 0)
        
    def test_user_cannot_access_other_users_location(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Try to access user2's location
        url = reverse('location-detail', args=[self.location2.location_id])
        response = self.client.get(url)
        
        # Check response (should be forbidden or not found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_set_default_location(self):
        # Create another location for user1
        location3 = Location.objects.create(
            user=self.user1,
            location_name="School",
            longitude=36.0800,
            latitude=-0.2900,
            is_default=False
        )
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # Set the new location as default
        url = reverse('location-set-default', args=[location3.location_id])
        response = self.client.post(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_default'])
        
        # Refresh location1 from database
        self.location1.refresh_from_db()
        
        # Original default location should no longer be default
        self.assertFalse(self.location1.is_default)
