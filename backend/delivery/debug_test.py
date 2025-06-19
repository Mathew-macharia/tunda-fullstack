from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json

from users.models import User
from locations.models import Location
from orders.models import Order, OrderItem
from payments.models import PaymentMethod
from products.models import Product, ProductListing, ProductCategory
from farms.models import Farm
from delivery.models import Vehicle, Delivery, DeliveryRoute


class DeliveryRouteDebugTestCase(APITestCase):
    """Debug test case for the DeliveryRoute API endpoint"""
    
    def setUp(self):
        # Create users
        self.rider = User.objects.create_user(
            phone_number="+1234567890",
            email="rider@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider",
            user_role="rider"
        )
        
        # Create locations
        self.location1 = Location.objects.create(
            user=self.rider,
            location_name="Home",
            sub_location="Test Area 1",
            landmark="Test Landmark 1",
            latitude=Decimal('1.2345'),
            longitude=Decimal('36.7890'),
            is_default=True
        )
        
        self.location2 = Location.objects.create(
            user=self.rider,
            location_name="Office",
            sub_location="Test Area 2",
            landmark="Test Landmark 2",
            latitude=Decimal('1.3456'),
            longitude=Decimal('36.8901'),
            is_default=False
        )
        
        # Setup API client
        self.client = APIClient()
    
    def test_debug_route_creation(self):
        """Debug the route creation test"""
        self.client.force_authenticate(user=self.rider)
        data = {
            'rider': self.rider.user_id,
            'route_name': 'New Route',
            'route_locations': [self.location1.location_id, self.location2.location_id],
            'estimated_time_hours': '2.00',
            'is_active': True
        }
        
        response = self.client.post(reverse('delivery-route-list'), data)
        
        print("\n\nDEBUG RESPONSE:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        # Test will fail but we'll see the error
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DeliveryDebugTestCase(APITestCase):
    """Debug test case for the Delivery API endpoint"""
    
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            phone_number="+1122334455",
            email="admin@example.com",
            password="testpassword",
            first_name="Admin",
            last_name="User",
            user_role="admin"
        )
        
        self.rider = User.objects.create_user(
            phone_number="+1234567890",
            email="rider@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider",
            user_role="rider"
        )
        
        self.customer = User.objects.create_user(
            phone_number="+0987654321",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create a location
        self.location = Location.objects.create(
            user=self.customer,
            location_name="Home",
            sub_location="Test Area",
            landmark="Test Landmark",
            latitude=Decimal('1.2345'),
            longitude=Decimal('36.7890'),
            is_default=True
        )
        
        # Create a payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="Mpesa",
            mpesa_phone="+0987654321",
            is_default=True
        )
        
        # Create a product category
        self.category = ProductCategory.objects.create(
            category_name="Test Category",
            description="A test category"
        )
        
        # Create a product
        self.product = Product.objects.create(
            category=self.category,
            product_name="Test Product",
            unit_of_measure="kg"
        )
        
        # Create a farmer
        self.farmer = User.objects.create_user(
            phone_number="+3456789012",
            email="farmer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Farmer",
            user_role="farmer"
        )
        
        # Create a farm
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name="Test Farm",
            location=self.location,
            farm_description="A test farm"
        )
        
        # Create a product listing
        self.listing = ProductListing.objects.create(
            farm=self.farm,
            farmer=self.farmer,
            product=self.product,
            quantity_available=Decimal('100.00'),
            current_price=Decimal('50.00'),
            quality_grade="premium",
            listing_status="available"
        )
        
        # Create an order
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            payment_method=self.payment_method,
            total_amount=Decimal('50.00'),
            delivery_fee=Decimal('10.00'),
            order_status="confirmed",
            payment_status="paid",
            estimated_delivery_date=timezone.now().date()
        )
        
        # Create a vehicle
        self.vehicle = Vehicle.objects.create(
            rider=self.rider,
            vehicle_type="motorcycle",
            registration_number="MC123",
            capacity_kg=Decimal('50.00'),
            description="Test motorcycle",
            is_active=True
        )
        
        # Setup API client
        self.client = APIClient()
    
    def test_debug_rider_create_delivery(self):
        """Debug the rider cannot create delivery test"""
        # Create another order
        order2 = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            payment_method=self.payment_method,
            total_amount=Decimal('75.00'),
            delivery_fee=Decimal('10.00'),
            order_status="confirmed",
            payment_status="paid",
            estimated_delivery_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.rider)
        data = {
            'order': order2.order_id,
            'rider': self.rider.user_id,
            'vehicle': self.vehicle.vehicle_id,
            'delivery_status': 'pending_pickup',
            'delivery_notes': 'New delivery notes'
        }
        
        response = self.client.post(reverse('delivery-list'), data)
        
        print("\n\nDEBUG DELIVERY RESPONSE:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        # Test will fail but we'll see the error
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
