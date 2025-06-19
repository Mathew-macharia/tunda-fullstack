from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from users.models import User
from locations.models import Location
from orders.models import Order, OrderItem
from payments.models import PaymentMethod
from products.models import Product, ProductListing, ProductCategory
from farms.models import Farm
from .models import Vehicle, Delivery, DeliveryRoute


class VehicleAPITestCase(APITestCase):
    """Test case for the Vehicle API endpoints"""
    
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
        
        self.rider2 = User.objects.create_user(
            phone_number="+2345678901",
            email="rider2@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider2",
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
        
        # Create a test vehicle
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
    
    def test_rider_list_own_vehicle(self):
        """Test that a rider can list their own vehicle"""
        self.client.force_authenticate(user=self.rider)
        response = self.client.get(reverse('vehicle-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vehicle_id'], self.vehicle.vehicle_id)
    
    def test_admin_list_all_vehicles(self):
        """Test that an admin can list all vehicles"""
        # Create another vehicle
        vehicle2 = Vehicle.objects.create(
            rider=self.rider2,
            vehicle_type="bicycle",
            registration_number="BC456",
            capacity_kg=Decimal('20.00'),
            description="Test bicycle",
            is_active=True
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('vehicle-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_customer_cannot_access_vehicles(self):
        """Test that a customer cannot access vehicles"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('vehicle-list'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_rider_create_vehicle(self):
        """Test that a rider can create their own vehicle"""
        self.client.force_authenticate(user=self.rider2)
        data = {
            'rider': self.rider2.user_id,  # Explicitly include rider ID
            'vehicle_type': 'bicycle',
            'registration_number': 'BC456',
            'capacity_kg': '20.00',
            'description': 'Test bicycle'
        }
        
        response = self.client.post(reverse('vehicle-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['vehicle_type'], 'bicycle')
        self.assertEqual(response.data['registration_number'], 'BC456')
        self.assertEqual(Vehicle.objects.count(), 2)
    
    def test_rider_update_own_vehicle(self):
        """Test that a rider can update their own vehicle"""
        self.client.force_authenticate(user=self.rider)
        data = {
            'description': 'Updated description',
            'capacity_kg': '60.00'
        }
        
        response = self.client.patch(
            reverse('vehicle-detail', args=[self.vehicle.vehicle_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['capacity_kg'], '60.00')
    
    def test_rider_cannot_update_other_vehicle(self):
        """Test that a rider cannot update another rider's vehicle"""
        self.client.force_authenticate(user=self.rider2)
        data = {
            'description': 'Unauthorized update'
        }
        
        response = self.client.patch(
            reverse('vehicle-detail', args=[self.vehicle.vehicle_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_update_any_vehicle(self):
        """Test that an admin can update any vehicle"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'description': 'Admin updated description'
        }
        
        response = self.client.patch(
            reverse('vehicle-detail', args=[self.vehicle.vehicle_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Admin updated description')
    
    def test_toggle_vehicle_active(self):
        """Test toggling a vehicle's active status"""
        self.client.force_authenticate(user=self.rider)
        
        response = self.client.patch(
            reverse('vehicle-toggle-active', args=[self.vehicle.vehicle_id])
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])  # Should be toggled to False


class DeliveryAPITestCase(APITestCase):
    """Test case for the Delivery API endpoints"""
    
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
        
        self.farmer = User.objects.create_user(
            phone_number="+3456789012",
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
            mpesa_phone="+0987654321",
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
            order_status="confirmed",
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
        
        # Setup API client
        self.client = APIClient()
    
    def test_admin_list_all_deliveries(self):
        """Test that an admin can list all deliveries"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('delivery-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_rider_list_own_deliveries(self):
        """Test that a rider can list their own deliveries"""
        self.client.force_authenticate(user=self.rider)
        response = self.client.get(reverse('delivery-my-deliveries'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['delivery_id'], self.delivery.delivery_id)
    
    def test_customer_list_own_deliveries(self):
        """Test that a customer can list deliveries for their orders"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('delivery-my-orders-delivery'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['delivery_id'], self.delivery.delivery_id)
    
    def test_admin_create_delivery(self):
        """Test that an admin can create a delivery"""
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
        
        self.client.force_authenticate(user=self.admin)
        data = {
            'order': order2.order_id,
            'rider': self.rider.user_id,
            'vehicle': self.vehicle.vehicle_id,
            'delivery_status': 'pending_pickup',
            'delivery_notes': 'New delivery notes'
        }
        
        response = self.client.post(reverse('delivery-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Delivery.objects.count(), 2)
    
    def test_rider_cannot_create_delivery(self):
        """Test that a rider cannot create a delivery"""
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
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_rider_update_delivery_status(self):
        """Test that a rider can update the status of their delivery"""
        self.client.force_authenticate(user=self.rider)
        data = {
            'delivery_status': 'on_the_way',
            'delivery_notes': 'On the way to customer'
        }
        
        response = self.client.patch(
            reverse('delivery-update-status', args=[self.delivery.delivery_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery_status'], 'on_the_way')
        self.assertEqual(response.data['delivery_notes'], 'On the way to customer')
        self.assertIsNotNone(response.data['pickup_time'])
    
    def test_invalid_delivery_status_transition(self):
        """Test that invalid status transitions are rejected"""
        self.client.force_authenticate(user=self.rider)
        data = {
            'delivery_status': 'delivered'  # Invalid transition from pending_pickup to delivered
        }
        
        response = self.client.patch(
            reverse('delivery-update-status', args=[self.delivery.delivery_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeliveryRouteAPITestCase(APITestCase):
    """Test case for the DeliveryRoute API endpoints"""
    
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
        
        # Setup API client
        self.client = APIClient()
    
    def test_rider_list_own_routes(self):
        """Test that a rider can list their own routes"""
        self.client.force_authenticate(user=self.rider)
        response = self.client.get(reverse('delivery-route-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['route_id'], self.route.route_id)
    
    def test_admin_list_all_routes(self):
        """Test that an admin can list all routes"""
        # Create another rider and route
        rider2 = User.objects.create_user(
            phone_number="+2345678901",
            email="rider2@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Rider2",
            user_role="rider"
        )
        
        route2 = DeliveryRoute.objects.create(
            rider=rider2,
            route_name="Test Route 2",
            route_locations=[self.location1.location_id],
            estimated_time_hours=Decimal('1.0'),
            is_active=True
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('delivery-route-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_customer_cannot_access_routes(self):
        """Test that a customer cannot access routes"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('delivery-route-list'))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_rider_create_route(self):
        """Test that a rider can create a route"""
        self.client.force_authenticate(user=self.rider)
        
        # Use json.dumps to ensure route_locations is properly formatted as JSON string
        import json
        data = {
            'rider': self.rider.user_id,  # Explicitly include rider ID
            'route_name': 'New Route',
            'route_locations': json.dumps([self.location1.location_id, self.location2.location_id]),
            'estimated_time_hours': '2.00',
            'is_active': True
        }
        
        response = self.client.post(reverse('delivery-route-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['route_name'], 'New Route')
        self.assertEqual(DeliveryRoute.objects.count(), 2)
    
    def test_rider_update_own_route(self):
        """Test that a rider can update their own route"""
        self.client.force_authenticate(user=self.rider)
        data = {
            'route_name': 'Updated Route Name',
            'estimated_time_hours': '2.00'
        }
        
        response = self.client.patch(
            reverse('delivery-route-detail', args=[self.route.route_id]),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['route_name'], 'Updated Route Name')
        self.assertEqual(response.data['estimated_time_hours'], '2.00')
    
    def test_get_active_routes(self):
        """Test getting active routes"""
        # Create an inactive route
        inactive_route = DeliveryRoute.objects.create(
            rider=self.rider,
            route_name="Inactive Route",
            route_locations=[self.location1.location_id],
            estimated_time_hours=Decimal('1.0'),
            is_active=False
        )
        
        self.client.force_authenticate(user=self.rider)
        response = self.client.get(reverse('delivery-route-active-routes'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the active route
        self.assertEqual(response.data[0]['route_id'], self.route.route_id)
    
    def test_toggle_route_active(self):
        """Test toggling a route's active status"""
        self.client.force_authenticate(user=self.rider)
        
        response = self.client.patch(
            reverse('delivery-route-toggle-active', args=[self.route.route_id])
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])  # Should be toggled to False
