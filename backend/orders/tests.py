from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from products.models import Product, ProductListing, ProductCategory, Farm
from locations.models import Location
from carts.models import Cart, CartItem
from .models import Order, OrderItem


class OrderAPITestCase(APITestCase):
    """Test case for the Order API"""
    
    def setUp(self):
        """Set up test data"""
        # Create customer user
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            phone_number='+254712345678',
            password='testpassword',
            user_role='customer',
            first_name='Test',
            last_name='Customer'
        )
        
        # Create farmer user
        self.farmer_user = User.objects.create_user(
            email='farmer@example.com',
            phone_number='+254712345679',
            password='testpassword',
            user_role='farmer',
            first_name='Test',
            last_name='Farmer'
        )
        
        # Create location for customer
        self.customer_location = Location.objects.create(
            user=self.customer_user,
            location_name='Home',
            sub_location='Test Area',
            landmark='123 Test St, Nairobi',
            latitude=1.2345,
            longitude=36.7890,
            is_default=True
        )
        
        # Create farm for farmer
        self.farm = Farm.objects.create(
            farm_name='Test Farm',
            farmer=self.farmer_user,
            farm_description='A test farm',
            location=Location.objects.create(
                user=self.farmer_user,
                location_name='Farm',
                sub_location='Farm Area',
                landmark='456 Farm Rd, Nairobi',
                latitude=1.2346,
                longitude=36.7891,
                is_default=True
            )
        )
        
        # Create category
        self.category = ProductCategory.objects.create(
            category_name='Vegetables',
            description='Fresh vegetables'
        )
        
        # Create product
        self.kale = Product.objects.create(
            product_name='Kale',
            description='Fresh kale',
            category=self.category,
            unit_of_measure='kg'
        )
        
        # Create product listing
        self.kale_listing = ProductListing.objects.create(
            farm=self.farm,
            farmer=self.farmer_user,
            product=self.kale,
            notes='Organic kale',
            quantity_available=Decimal('50.0'),
            min_order_quantity=Decimal('2.0'),
            current_price=Decimal('150.00'),
            listing_status='available',
            quality_grade='premium'
        )
        
        # Create a cart for the customer
        self.cart = Cart.objects.create(customer=self.customer_user)
        
        # Add kale to the cart
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            listing=self.kale_listing,
            quantity=Decimal('5.0'),
            price_at_addition=self.kale_listing.current_price
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_create_order_unauthorized(self):
        """Test creating an order without authentication"""
        response = self.client.post(
            reverse('order-list'),
            {
                'delivery_location_id': self.customer_location.location_id,
                'estimated_delivery_date': timezone.now().date().isoformat(),
                'delivery_time_slot': 'morning',
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_order_with_empty_cart(self):
        """Test creating an order with an empty cart"""
        # Clear the cart
        self.cart_item.delete()
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        response = self.client.post(
            reverse('order-list'),
            {
                'delivery_location_id': self.customer_location.location_id,
                'estimated_delivery_date': timezone.now().date().isoformat(),
                'delivery_time_slot': 'morning',
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cart', response.data.get('error', ''))
    
    def test_create_order_success(self):
        """Test successfully creating an order from a cart"""
        # Make sure the inventory is sufficient
        self.kale_listing.quantity_available = Decimal('50.0')
        self.kale_listing.save()
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        # Get initial inventory
        initial_inventory = self.kale_listing.quantity_available
        
        # Create the order
        response = self.client.post(
            reverse('order-list'),
            {
                'delivery_location_id': self.customer_location.location_id,
                'payment_method_id': 999,  # Use 999 for COD as per the serializer
                'estimated_delivery_date': timezone.now().date().isoformat(),
                'delivery_time_slot': 'morning',
                'special_instructions': 'Please deliver in the morning.',
            },
            format='json'
        )
        
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that an order was created
        order = Order.objects.get(order_id=response.data['order_id'])
        self.assertEqual(order.customer, self.customer_user)
        self.assertEqual(order.delivery_location, self.customer_location)
        self.assertEqual(order.total_amount, Decimal('5.0') * self.kale_listing.current_price)
        
        # Check that order items were created
        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(order_items.count(), 1)
        order_item = order_items.first()
        self.assertEqual(order_item.listing, self.kale_listing)
        self.assertEqual(order_item.quantity, Decimal('5.0'))
        self.assertEqual(order_item.price_at_purchase, self.kale_listing.current_price)
        
        # Check that inventory was updated
        self.kale_listing.refresh_from_db()
        self.assertEqual(self.kale_listing.quantity_available, initial_inventory - Decimal('5.0'))
        
        # Check that cart was cleared
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())
    
    def test_create_order_insufficient_inventory(self):
        """Test creating an order with insufficient inventory"""
        # Set inventory lower than cart quantity
        self.kale_listing.quantity_available = Decimal('4.0')
        self.kale_listing.save()
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        # Create the order
        response = self.client.post(
            reverse('order-list'),
            {
                'delivery_location_id': self.customer_location.location_id,
                'estimated_delivery_date': timezone.now().date().isoformat(),
                'delivery_time_slot': 'morning',
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('inventory', response.data.get('error', ''))
    
    def test_customer_list_orders(self):
        """Test customer listing their orders"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='paid'
        )
        
        OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        # List orders
        response = self.client.get(reverse('order-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_id'], order.order_id)
    
    def test_customer_retrieve_order(self):
        """Test customer retrieving an order"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='paid'
        )
        
        OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        # Retrieve order
        response = self.client.get(reverse('order-detail', args=[order.order_id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_id'], order.order_id)
        self.assertEqual(len(response.data['items']), 1)
    
    def test_customer_cancel_order(self):
        """Test customer cancelling an order"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='pending'
        )
        
        # Set initial inventory
        self.kale_listing.quantity_available = Decimal('45.0')
        self.kale_listing.save()
        initial_inventory = self.kale_listing.quantity_available
        
        OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as customer
        self.client.force_authenticate(user=self.customer_user)
        
        # Cancel order
        response = self.client.post(reverse('order-cancel', args=[order.order_id]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh order
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'cancelled')
        
        # Check inventory was restored
        self.kale_listing.refresh_from_db()
        self.assertEqual(self.kale_listing.quantity_available, initial_inventory + Decimal('5.0'))
    
    def test_farmer_list_order_items(self):
        """Test farmer listing their order items"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='paid'
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as farmer
        self.client.force_authenticate(user=self.farmer_user)
        
        # List order items
        response = self.client.get(reverse('farmer-order-item-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['order_item_id'], order_item.order_item_id)
    
    def test_farmer_update_order_item_status(self):
        """Test farmer updating an order item status"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='paid'
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as farmer
        self.client.force_authenticate(user=self.farmer_user)
        
        # Update order item status to harvested
        response = self.client.patch(
            reverse('farmer-order-item-detail', args=[order_item.order_item_id]),
            {'item_status': 'harvested'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_status'], 'harvested')
        
        # Check item was updated
        order_item.refresh_from_db()
        self.assertEqual(order_item.item_status, 'harvested')
        
        # Update to packed
        response = self.client.patch(
            reverse('farmer-order-item-detail', args=[order_item.order_item_id]),
            {'item_status': 'packed'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_status'], 'packed')
        
        # Check item was updated
        order_item.refresh_from_db()
        self.assertEqual(order_item.item_status, 'packed')
        
        # Check if order status was updated
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'processing')
    
    def test_farmer_invalid_order_item_status_transition(self):
        """Test farmer making an invalid order item status transition"""
        # Create an order for testing
        order = Order.objects.create(
            customer=self.customer_user,
            delivery_location=self.customer_location,
            total_amount=Decimal('750.00'),
            order_status='confirmed',
            payment_status='paid'
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            listing=self.kale_listing,
            farmer=self.farmer_user,
            quantity=Decimal('5.0'),
            price_at_purchase=Decimal('150.00'),
            total_price=Decimal('750.00')
        )
        
        # Authenticate as farmer
        self.client.force_authenticate(user=self.farmer_user)
        
        # Try to update to packed directly
        response = self.client.patch(
            reverse('farmer-order-item-detail', args=[order_item.order_item_id]),
            {'item_status': 'packed'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('item_status', response.data)
