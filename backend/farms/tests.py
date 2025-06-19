from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Farm
from locations.models import Location
import json

User = get_user_model()

class FarmModelTests(TestCase):
    def setUp(self):
        # Create a farmer user
        self.farmer = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Farmer",
            last_name="Test",
            user_role="farmer"
        )
        
        # Create a location for the farmer
        self.location = Location.objects.create(
            user=self.farmer,
            location_name="Farm Location",
            latitude=-0.2833,
            longitude=36.0699,
            is_default=True
        )
        
    def test_create_farm(self):
        farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name="Test Farm",
            location=self.location,
            total_acreage=5.5,
            farm_description="A test farm for crops",
            farm_photos=["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"],
            is_certified_organic=True,
            weather_zone="highland"
        )
        
        self.assertEqual(farm.farm_name, "Test Farm")
        self.assertEqual(farm.farmer, self.farmer)
        self.assertEqual(farm.location, self.location)
        self.assertEqual(float(farm.total_acreage), 5.5)
        self.assertTrue(farm.is_certified_organic)
        self.assertEqual(farm.weather_zone, "highland")
        self.assertEqual(len(farm.farm_photos), 2)
        self.assertEqual(farm.farm_photos[0], "http://example.com/photo1.jpg")

class FarmAPITests(APITestCase):
    def setUp(self):
        # Create a farmer user
        self.farmer = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Farmer",
            last_name="Test",
            user_role="farmer"
        )
        
        # Create another farmer user
        self.other_farmer = User.objects.create_user(
            phone_number="0787654321",
            password="testpass456",
            first_name="Other",
            last_name="Farmer",
            user_role="farmer"
        )
        
        # Create a customer user (non-farmer)
        self.customer = User.objects.create_user(
            phone_number="0723456789",
            password="testpass789",
            first_name="Customer",
            last_name="Test",
            user_role="customer"
        )
        
        # Create locations for the farmers
        self.location1 = Location.objects.create(
            user=self.farmer,
            location_name="Farm Location 1",
            latitude=-0.2833,
            longitude=36.0699,
            is_default=True
        )
        
        self.location2 = Location.objects.create(
            user=self.other_farmer,
            location_name="Farm Location 2",
            latitude=-0.2900,
            longitude=36.0800,
            is_default=True
        )
        
        # Create a test farm for the first farmer
        self.farm1 = Farm.objects.create(
            farmer=self.farmer,
            farm_name="Test Farm 1",
            location=self.location1,
            total_acreage=5.5,
            farm_description="A test farm for crops",
            farm_photos=["http://example.com/photo1.jpg"],
            is_certified_organic=True,
            weather_zone="highland"
        )
        
        # Create a test farm for the other farmer
        self.farm2 = Farm.objects.create(
            farmer=self.other_farmer,
            farm_name="Test Farm 2",
            location=self.location2,
            total_acreage=10.0,
            farm_description="Another test farm",
            farm_photos=["http://example.com/photo2.jpg"],
            is_certified_organic=False,
            weather_zone="midland"
        )
        
        self.client = APIClient()
        
    def test_list_farms_as_farmer(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Get list of farms
        url = reverse('farm-list')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own farm
        self.assertEqual(response.data[0]['farm_name'], 'Test Farm 1')
        
    def test_create_farm_as_farmer(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Create new farm
        url = reverse('farm-list')
        data = {
            'farm_name': 'New Test Farm',
            'location': self.location1.location_id,
            'total_acreage': 7.5,
            'farm_description': 'A new test farm',
            'farm_photos': ["http://example.com/photo3.jpg"],
            'is_certified_organic': False,
            'weather_zone': 'lowland'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Farm.objects.filter(farmer=self.farmer).count(), 2)
        self.assertEqual(response.data['farm_name'], 'New Test Farm')
        
    def test_create_farm_with_other_farmer_location(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Try to create farm with other farmer's location
        url = reverse('farm-list')
        data = {
            'farm_name': 'Invalid Farm',
            'location': self.location2.location_id,  # Other farmer's location
            'total_acreage': 7.5,
            'farm_description': 'This should fail',
            'is_certified_organic': False,
            'weather_zone': 'lowland'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check response - should fail validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_farm_as_customer(self):
        # Authenticate as the customer (non-farmer)
        self.client.force_authenticate(user=self.customer)
        
        # Try to create farm
        url = reverse('farm-list')
        data = {
            'farm_name': 'Invalid Farm',
            'location': self.location1.location_id,
            'total_acreage': 7.5,
            'farm_description': 'This should fail',
            'is_certified_organic': False,
            'weather_zone': 'lowland'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check response - should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_retrieve_farm(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Get farm details
        url = reverse('farm-detail', args=[self.farm1.farm_id])
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['farm_name'], 'Test Farm 1')
        self.assertEqual(float(response.data['total_acreage']), 5.5)
        
    def test_update_farm(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Update farm
        url = reverse('farm-detail', args=[self.farm1.farm_id])
        data = {
            'farm_name': 'Updated Farm Name',
            'farm_description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['farm_name'], 'Updated Farm Name')
        self.assertEqual(response.data['farm_description'], 'Updated description')
        
    def test_delete_farm(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Delete farm
        url = reverse('farm-detail', args=[self.farm1.farm_id])
        response = self.client.delete(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Farm.objects.filter(farmer=self.farmer).count(), 0)
        
    def test_cannot_access_other_farmers_farm(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Try to access other farmer's farm
        url = reverse('farm-detail', args=[self.farm2.farm_id])
        response = self.client.get(url)
        
        # Check response - should not be found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_filter_organic_farms(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Filter organic farms
        url = reverse('farm-organic')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own organic farm
        self.assertEqual(response.data[0]['farm_name'], 'Test Farm 1')
        
    def test_filter_by_weather_zone(self):
        # Authenticate as the farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Filter farms by weather zone
        url = reverse('farm-by-weather-zone') + '?zone=highland'
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own farm in highland zone
        self.assertEqual(response.data[0]['farm_name'], 'Test Farm 1')
