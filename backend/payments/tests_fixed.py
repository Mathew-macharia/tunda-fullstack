from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone

from .models import PaymentMethod, PaymentTransaction
from orders.models import Order, OrderItem
from products.models import Product, ProductListing, ProductCategory
from locations.models import Location
from farms.models import Farm
from users.models import User
from decimal import Decimal

class PaymentMethodModelTestCase(TestCase):
    """Test case for the PaymentMethod model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            phone_number="+1234567890",
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            user_role="customer"
        )
        
        # Create test payment methods
        self.mpesa_method = PaymentMethod.objects.create(
            user=self.user,
            payment_type="Mpesa",
            mpesa_phone="+1234567890",
            is_default=True
        )
        
        self.cod_method = PaymentMethod.objects.create(
            user=self.user,
            payment_type="CashOnDelivery",
            is_default=False
        )
    
    def test_payment_method_creation(self):
        """Test creating a payment method"""
        self.assertEqual(PaymentMethod.objects.count(), 2)
        self.assertEqual(self.mpesa_method.user, self.user)
        self.assertEqual(self.mpesa_method.payment_type, "Mpesa")
        self.assertEqual(self.mpesa_method.mpesa_phone, "+1234567890")
        self.assertTrue(self.mpesa_method.is_default)
    
    def test_default_payment_method(self):
        """Test that only one payment method is default"""
        # Initial state: mpesa_method is default, cod_method is not
        self.assertTrue(self.mpesa_method.is_default)
        self.assertFalse(self.cod_method.is_default)
        
        # Set cod_method as default
        self.cod_method.is_default = True
        self.cod_method.save()
        
        # Refresh from database
        self.mpesa_method.refresh_from_db()
        self.cod_method.refresh_from_db()
        
        # Now cod_method should be default, and mpesa_method should not
        self.assertFalse(self.mpesa_method.is_default)
        self.assertTrue(self.cod_method.is_default)

class PaymentTransactionModelTestCase(TestCase):
    """Test case for the PaymentTransaction model"""
    
    def setUp(self):
        # Create a test customer
        self.customer = User.objects.create_user(
            phone_number="+1234567890",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create a test farmer
        self.farmer = User.objects.create_user(
            phone_number="+0987654321",
            email="farmer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Farmer",
            user_role="farmer"
        )
        
        # Create a test location
        self.location = Location.objects.create(
            user=self.customer,
            location_name="Home",
            sub_location="Test Area",
            landmark="123 Test St",
            latitude=Decimal('1.2345'),
            longitude=Decimal('36.7890'),
            is_default=True
        )
        
        # Create a test farm
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
        
        # Create a test product
        self.product = Product.objects.create(
            category=self.category,
            product_name="Test Product",
            unit_of_measure="kg"
        )
        
        # Create a test product listing
        self.listing = ProductListing.objects.create(
            farm=self.farm,
            farmer=self.farmer,
            product=self.product,
            quantity_available=Decimal('10.0'),
            current_price=Decimal('100.0'),
            quality_grade="premium",
            listing_status="available"
        )
        
        # Create a test order
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('100.0'),
            delivery_fee=Decimal('50.0'),
            order_status="pending_payment",
            payment_status="pending",
            estimated_delivery_date=timezone.now().date()
        )
        
        # Create a test order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            listing=self.listing,
            farmer=self.farmer,
            quantity=Decimal('1.0'),
            price_at_purchase=Decimal('100.0'),
            total_price=Decimal('100.0')
        )
        
        # Create a test payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="Mpesa",
            mpesa_phone="+1234567890",
            is_default=True
        )
        
        # Create a test payment transaction
        self.transaction = PaymentTransaction.objects.create(
            order=self.order,
            payment_method=self.payment_method,
            amount=Decimal('150.0'),  # Total + delivery fee
            payment_status="pending"
        )
    
    def test_payment_transaction_creation(self):
        """Test creating a payment transaction"""
        self.assertEqual(PaymentTransaction.objects.count(), 1)
        self.assertEqual(self.transaction.order, self.order)
        self.assertEqual(self.transaction.payment_method, self.payment_method)
        self.assertEqual(self.transaction.amount, Decimal('150.0'))
        self.assertEqual(self.transaction.payment_status, "pending")
    
    def test_complete_payment(self):
        """Test completing a payment and updating order status"""
        # Initial state
        self.assertEqual(self.order.payment_status, "pending")
        self.assertEqual(self.order.order_status, "pending_payment")
        
        # Complete the payment
        self.transaction.payment_status = "completed"
        self.transaction.payment_date = timezone.now()
        self.transaction.transaction_code = "TEST123"
        self.transaction.save()
        
        # Update order status
        self.transaction.update_order_status()
        
        # Refresh order from database
        self.order.refresh_from_db()
        
        # Check that order status is updated
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.order_status, "confirmed")
    
    def test_failed_payment(self):
        """Test failed payment and order status update"""
        # Initial state
        self.assertEqual(self.order.payment_status, "pending")
        
        # Fail the payment
        self.transaction.payment_status = "failed"
        self.transaction.failure_reason = "Insufficient funds"
        self.transaction.save()
        
        # Update order status
        self.transaction.update_order_status()
        
        # Refresh order from database
        self.order.refresh_from_db()
        
        # Check that order status is updated
        self.assertEqual(self.order.payment_status, "failed")
        self.assertEqual(self.order.order_status, "pending_payment")

class PaymentMethodAPITestCase(APITestCase):
    """Test case for the PaymentMethod API"""
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            phone_number="+1234567890",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        self.other_customer = User.objects.create_user(
            phone_number="+0987654321",
            email="other@example.com",
            password="testpassword",
            first_name="Other",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create a test payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="Mpesa",
            mpesa_phone="+1234567890",
            is_default=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_list_payment_methods(self):
        """Test listing a user's payment methods"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('payment-method-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_payment_method(self):
        """Test creating a new payment method"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'payment_type': 'CashOnDelivery',
            'is_default': False
        }
        response = self.client.post(reverse('payment-method-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentMethod.objects.count(), 2)
        
        # Check that the new method is not default (since another one already is)
        new_method = PaymentMethod.objects.get(payment_type='CashOnDelivery')
        self.assertFalse(new_method.is_default)
    
    def test_create_mpesa_without_phone(self):
        """Test creating an M-Pesa payment method without a phone number"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'payment_type': 'Mpesa',
            'is_default': False
        }
        response = self.client.post(reverse('payment-method-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mpesa_phone', response.data)
    
    def test_set_default_payment_method(self):
        """Test setting a payment method as default"""
        # Create a second non-default payment method
        second_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="CashOnDelivery",
            is_default=False
        )
        
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(reverse('payment-method-set-default', args=[second_method.payment_method_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.payment_method.refresh_from_db()
        second_method.refresh_from_db()
        
        # Check that defaults were updated
        self.assertFalse(self.payment_method.is_default)
        self.assertTrue(second_method.is_default)
    
    def test_access_other_user_payment_method(self):
        """Test that a user cannot access another user's payment methods"""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.get(reverse('payment-method-detail', args=[self.payment_method.payment_method_id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class PaymentTransactionAPITestCase(APITestCase):
    """Test case for the PaymentTransaction API"""
    
    def setUp(self):
        # Create a test customer
        self.customer = User.objects.create_user(
            phone_number="+1234567890",
            email="customer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Customer",
            user_role="customer"
        )
        
        # Create a test farmer
        self.farmer = User.objects.create_user(
            phone_number="+0987654321",
            email="farmer@example.com",
            password="testpassword",
            first_name="Test",
            last_name="Farmer",
            user_role="farmer"
        )
        
        # Create an admin user
        self.admin = User.objects.create_user(
            phone_number="+1122334455",
            email="admin@example.com",
            password="testpassword",
            first_name="Admin",
            last_name="User",
            user_role="admin"
        )
        
        # Create a test location
        self.location = Location.objects.create(
            user=self.customer,
            location_name="Home",
            sub_location="Test Area",
            landmark="123 Test St",
            latitude=Decimal('1.2345'),
            longitude=Decimal('36.7890'),
            is_default=True
        )
        
        # Create a test farm
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name="Test Farm",
            location=self.location,
            farm_description="A test farm"
        )
        
        # Create a product category
        self.category = ProductCategory.objects.create(
            category_name="Test API Category",
            description="A test category for API"
        )
        
        # Create a test product
        self.product = Product.objects.create(
            category=self.category,
            product_name="Test Product",
            unit_of_measure="kg"
        )
        
        # Create a test product listing
        self.listing = ProductListing.objects.create(
            farm=self.farm,
            farmer=self.farmer,
            product=self.product,
            quantity_available=Decimal('10.0'),
            current_price=Decimal('100.0'),
            quality_grade="premium",
            listing_status="available"
        )
        
        # Create a test order
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('100.0'),
            delivery_fee=Decimal('50.0'),
            order_status="pending_payment",
            payment_status="pending",
            estimated_delivery_date=timezone.now().date()
        )
        
        # Create a test order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            listing=self.listing,
            farmer=self.farmer,
            quantity=Decimal('1.0'),
            price_at_purchase=Decimal('100.0'),
            total_price=Decimal('100.0')
        )
        
        # Create a test payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type="Mpesa",
            mpesa_phone="+1234567890",
            is_default=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_create_transaction(self):
        """Test creating a payment transaction"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'order': self.order.order_id,
            'payment_method': self.payment_method.payment_method_id,
            'amount': '150.00'  # Total + delivery fee
        }
        response = self.client.post(reverse('payment-transaction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentTransaction.objects.count(), 1)
    
    def test_create_transaction_wrong_amount(self):
        """Test creating a transaction with the wrong amount"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'order': self.order.order_id,
            'payment_method': self.payment_method.payment_method_id,
            'amount': '100.00'  # Wrong amount (should be 150.00)
        }
        response = self.client.post(reverse('payment-transaction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_simulate_payment(self):
        """Test simulating a successful payment"""
        # Create a pending transaction
        transaction = PaymentTransaction.objects.create(
            order=self.order,
            payment_method=self.payment_method,
            amount=Decimal('150.0'),
            payment_status="pending"
        )
        
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(reverse('payment-transaction-simulate-payment', args=[transaction.transaction_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        transaction.refresh_from_db()
        self.order.refresh_from_db()
        
        # Check that transaction and order were updated
        self.assertEqual(transaction.payment_status, "completed")
        self.assertIsNotNone(transaction.payment_date)
        self.assertIsNotNone(transaction.transaction_code)
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.order_status, "confirmed")
    
    def test_payment_callback(self):
        """Test the payment callback endpoint"""
        # Create a pending transaction
        transaction = PaymentTransaction.objects.create(
            order=self.order,
            payment_method=self.payment_method,
            amount=Decimal('150.0'),
            payment_status="pending"
        )
        
        # No authentication required for callback
        data = {
            'transaction_id': transaction.transaction_id,
            'transaction_code': 'MPESA123456',
            'payment_status': 'completed'
        }
        response = self.client.post(reverse('payment-transaction-callback'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        transaction.refresh_from_db()
        self.order.refresh_from_db()
        
        # Check that transaction and order were updated
        self.assertEqual(transaction.payment_status, "completed")
        self.assertEqual(transaction.transaction_code, "MPESA123456")
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.order_status, "confirmed")
    
    def test_admin_list_all_transactions(self):
        """Test that admins can list all transactions"""
        # Create a transaction
        transaction = PaymentTransaction.objects.create(
            order=self.order,
            payment_method=self.payment_method,
            amount=Decimal('150.0'),
            payment_status="pending"
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('payment-transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
