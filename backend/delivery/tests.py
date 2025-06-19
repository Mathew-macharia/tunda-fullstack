from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

from users.models import User
from locations.models import Location
from orders.models import Order, OrderItem
from payments.models import PaymentMethod
from products.models import Product, ProductListing, ProductCategory
from farms.models import Farm
from .models import Vehicle, Delivery, DeliveryRoute


class VehicleModelTestCase(TestCase):
    """Test case for the Vehicle model"""
    
    def setUp(self):
        # Create a rider user
        self.rider = User.objects.create_user(
            phone_number="+1234567890",
            email="rider@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider",
            user_role="rider"
        )
        
        # Create a non-rider user
        self.customer = User.objects.create_user(
            phone_number="+0987654321",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create a test vehicle
        self.vehicle = Vehicle.objects.create(
            rider=self.rider,
            vehicle_type="motorcycle",
            registration_number="MC123",
            capacity_kg=Decimal('50.00'),
            description="Test motorcycle",
            is_active=True
        )
    
    def test_vehicle_creation(self):
        """Test creating a vehicle"""
        self.assertEqual(Vehicle.objects.count(), 1)
        self.assertEqual(self.vehicle.rider, self.rider)
        self.assertEqual(self.vehicle.vehicle_type, "motorcycle")
        self.assertEqual(self.vehicle.registration_number, "MC123")
        self.assertEqual(self.vehicle.capacity_kg, Decimal('50.00'))
        self.assertEqual(self.vehicle.description, "Test motorcycle")
        self.assertTrue(self.vehicle.is_active)
    
    def test_vehicle_str_representation(self):
        """Test the string representation of a vehicle"""
        expected_str = f"{self.rider.get_full_name()}'s Motorcycle (MC123)"
        self.assertEqual(str(self.vehicle), expected_str)
    
    def test_vehicle_creation_non_rider(self):
        """Test that only riders can have vehicles"""
        with self.assertRaises(ValidationError):
            Vehicle.objects.create(
                rider=self.customer,
                vehicle_type="bicycle",
                registration_number="BC456",
                capacity_kg=Decimal('20.00'),
                description="Test bicycle",
                is_active=True
            )


class DeliveryModelTestCase(TestCase):
    """Test case for the Delivery model"""
    
    def setUp(self):
        # Create users
        self.customer = User.objects.create_user(
            phone_number="+1234567890",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        self.rider = User.objects.create_user(
            phone_number="+0987654321",
            email="rider@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider",
            user_role="rider"
        )
        
        self.farmer = User.objects.create_user(
            phone_number="+1122334455",
            email="farmer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Farmer",
            user_role="farmer"
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
            mpesa_phone="+1234567890",
            is_default=True
        )
        
        # Create a farm
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name="Test Farm",
            location=self.location,
            farm_description="A test farm"
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
            order_status="confirmed",  # Confirmed order ready for delivery
            payment_status="paid",
            estimated_delivery_date=timezone.now().date()
        )
        
        # Create an order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            listing=self.listing,
            farmer=self.farmer,
            quantity=Decimal('1.00'),
            price_at_purchase=Decimal('50.00'),
            total_price=Decimal('50.00'),
            item_status="confirmed"
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
        
        # Create a delivery
        self.delivery = Delivery.objects.create(
            order=self.order,
            rider=self.rider,
            vehicle=self.vehicle,
            delivery_status="pending_pickup",
            delivery_notes="Test delivery notes"
        )
    
    def test_delivery_creation(self):
        """Test creating a delivery"""
        self.assertEqual(Delivery.objects.count(), 1)
        self.assertEqual(self.delivery.order, self.order)
        self.assertEqual(self.delivery.rider, self.rider)
        self.assertEqual(self.delivery.vehicle, self.vehicle)
        self.assertEqual(self.delivery.delivery_status, "pending_pickup")
        self.assertEqual(self.delivery.delivery_notes, "Test delivery notes")
        self.assertIsNone(self.delivery.pickup_time)
        self.assertIsNone(self.delivery.delivery_time)
    
    def test_delivery_str_representation(self):
        """Test the string representation of a delivery"""
        expected_str = f"Delivery #{self.delivery.delivery_id} for Order #{self.order.order_number}"
        self.assertEqual(str(self.delivery), expected_str)
    
    def test_delivery_status_update_to_on_the_way(self):
        """Test updating delivery status to 'on_the_way'"""
        self.delivery.delivery_status = "on_the_way"
        self.delivery.save()
        
        # Refresh from database
        self.delivery.refresh_from_db()
        self.order.refresh_from_db()
        
        # Check delivery and order status
        self.assertEqual(self.delivery.delivery_status, "on_the_way")
        self.assertEqual(self.order.order_status, "en_route")
        self.assertIsNotNone(self.delivery.pickup_time)
        self.assertIsNone(self.delivery.delivery_time)
    
    def test_delivery_status_update_to_delivered(self):
        """Test updating delivery status to 'delivered'"""
        self.delivery.delivery_status = "delivered"
        self.delivery.save()
        
        # Refresh from database
        self.delivery.refresh_from_db()
        self.order.refresh_from_db()
        self.order_item.refresh_from_db()
        
        # Check delivery, order and order item status
        self.assertEqual(self.delivery.delivery_status, "delivered")
        self.assertEqual(self.order.order_status, "delivered")
        self.assertEqual(self.order_item.item_status, "delivered")
        self.assertIsNotNone(self.delivery.delivery_time)
    
    def test_cash_on_delivery_payment_update(self):
        """Test that COD orders are marked paid on delivery"""
        # Change payment method to Cash on Delivery and update payment status
        cod_payment = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="CashOnDelivery",
            is_default=False
        )
        
        self.order.payment_method = cod_payment
        self.order.payment_status = "pending"
        self.order.save()
        
        # Update delivery status to delivered
        self.delivery.delivery_status = "delivered"
        self.delivery.save()
        
        # Refresh order from database
        self.order.refresh_from_db()
        
        # Check payment status is updated
        self.assertEqual(self.order.payment_status, "paid")


class DeliveryRouteModelTestCase(TestCase):
    """Test case for the DeliveryRoute model"""
    
    def setUp(self):
        # Create a rider user
        self.rider = User.objects.create_user(
            phone_number="+1234567890",
            email="rider@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider",
            user_role="rider"
        )
        
        # Create a non-rider user
        self.customer = User.objects.create_user(
            phone_number="+0987654321",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create locations
        self.location1 = Location.objects.create(
            user=self.customer,
            location_name="Home",
            sub_location="Test Area 1",
            landmark="Test Landmark 1",
            latitude=Decimal('1.2345'),
            longitude=Decimal('36.7890'),
            is_default=True
        )
        
        self.location2 = Location.objects.create(
            user=self.customer,
            location_name="Office",
            sub_location="Test Area 2",
            landmark="Test Landmark 2",
            latitude=Decimal('1.3456'),
            longitude=Decimal('36.8901'),
            is_default=False
        )
        
        # Create a delivery route
        self.route = DeliveryRoute.objects.create(
            rider=self.rider,
            route_name="Test Route",
            route_locations=[self.location1.location_id, self.location2.location_id],
            estimated_time_hours=Decimal('1.5'),
            is_active=True
        )
    
    def test_route_creation(self):
        """Test creating a delivery route"""
        self.assertEqual(DeliveryRoute.objects.count(), 1)
        self.assertEqual(self.route.rider, self.rider)
        self.assertEqual(self.route.route_name, "Test Route")
        self.assertEqual(self.route.route_locations, [self.location1.location_id, self.location2.location_id])
        self.assertEqual(self.route.estimated_time_hours, Decimal('1.5'))
        self.assertTrue(self.route.is_active)
    
    def test_route_str_representation(self):
        """Test the string representation of a route"""
        expected_str = f"Test Route (Rider: {self.rider.get_full_name()})"
        self.assertEqual(str(self.route), expected_str)
    
    def test_route_creation_non_rider(self):
        """Test that only riders can have delivery routes"""
        with self.assertRaises(ValidationError):
            DeliveryRoute.objects.create(
                rider=self.customer,
                route_name="Invalid Route",
                route_locations=[self.location1.location_id],
                estimated_time_hours=Decimal('1.0'),
                is_active=True
            )
