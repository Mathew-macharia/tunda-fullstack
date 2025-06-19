from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Payout
from users.models import User
from orders.models import Order
from locations.models import Location
from payments.models import PaymentMethod

class PayoutModelTestCase(TestCase):
    """Test case for the Payout model"""
    
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='0700000001',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.farmer = User.objects.create_user(
            phone_number='0700000002',
            email='farmer@example.com',
            first_name='Farmer',
            last_name='User',
            password='password',
            user_role='farmer'
        )
        
        self.customer = User.objects.create_user(
            phone_number='0700000004',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        # Create test location
        self.location = Location.objects.create(
            user=self.customer,
            location_name='Test Location',
            latitude=0.0,
            longitude=0.0,
            landmark='Test Landmark',
            is_default=True
        )
        
        # Create test payment method
        self.payment_method = PaymentMethod.objects.create(
            user=self.customer,
            payment_type='Mpesa',
            mpesa_phone='1234567890',
            is_default=True
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            payment_method=self.payment_method,
            total_amount=Decimal('50.00'),
            delivery_fee=Decimal('5.00'),
            order_status='delivered',
            payment_status='paid',
            estimated_delivery_date=timezone.now().date()
        )
    
    def test_create_payout(self):
        """Test creating a payout"""
        payout = Payout.objects.create(
            user=self.farmer,
            order=self.order,
            amount=Decimal('45.00'),
            status='pending',
            notes='Payout for order #123'
        )
        
        self.assertEqual(payout.user, self.farmer)
        self.assertEqual(payout.order, self.order)
        self.assertEqual(payout.amount, Decimal('45.00'))
        self.assertEqual(payout.status, 'pending')
        self.assertEqual(payout.notes, 'Payout for order #123')
        self.assertIsNone(payout.processed_date)
    
    def test_payout_string_representation(self):
        """Test the string representation of a payout"""
        payout = Payout.objects.create(
            user=self.farmer,
            amount=Decimal('100.00'),
            status='pending'
        )
        
        expected_str = f"Payout {payout.payout_id} - {self.farmer.phone_number} - {Decimal('100.00')}"
        self.assertEqual(str(payout), expected_str)


class PayoutAPITestCase(APITestCase):
    """Test case for the Payout API endpoints"""
    
    def setUp(self):
        # Create test client
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='0700000001',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.farmer = User.objects.create_user(
            phone_number='0700000002',
            email='farmer@example.com',
            first_name='Farmer',
            last_name='User',
            password='password',
            user_role='farmer'
        )
        
        self.rider = User.objects.create_user(
            phone_number='0700000003',
            email='rider@example.com',
            first_name='Rider',
            last_name='User',
            password='password',
            user_role='rider'
        )
        
        self.customer = User.objects.create_user(
            phone_number='0700000004',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        # Create test payouts
        self.farmer_payout = Payout.objects.create(
            user=self.farmer,
            amount=Decimal('100.00'),
            status='pending',
            notes='Farmer payout'
        )
        
        self.rider_payout = Payout.objects.create(
            user=self.rider,
            amount=Decimal('50.00'),
            status='pending',
            notes='Rider payout'
        )
    
    def test_list_payouts_as_admin(self):
        """Test listing all payouts as admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('payout-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_payouts_as_farmer(self):
        """Test listing payouts as farmer (should only see own payouts)"""
        self.client.force_authenticate(user=self.farmer)
        url = reverse('payout-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Convert both values to int to ensure consistent comparison
        self.assertEqual(int(response.data[0]['user']), int(self.farmer.user_id))
    
    def test_create_payout_as_admin(self):
        """Test creating a payout as admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('payout-list')
        data = {
            'user': self.farmer.user_id,
            'amount': '75.00',
            'status': 'pending',
            'notes': 'New farmer payout'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '75.00')
        self.assertEqual(Payout.objects.count(), 3)
    
    def test_create_payout_as_farmer_fails(self):
        """Test creating a payout as farmer (should fail)"""
        self.client.force_authenticate(user=self.farmer)
        url = reverse('payout-list')
        data = {
            'user': self.farmer.user_id,
            'amount': '75.00',
            'status': 'pending',
            'notes': 'Self-created payout'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_process_payout_as_admin(self):
        """Test processing a payout as admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('payout-process', args=[self.farmer_payout.payout_id])
        data = {'transaction_reference': 'TX123456789'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.farmer_payout.refresh_from_db()
        self.assertEqual(self.farmer_payout.status, 'processed')
        self.assertEqual(self.farmer_payout.transaction_reference, 'TX123456789')
        self.assertIsNotNone(self.farmer_payout.processed_date)
    
    def test_fail_payout_as_admin(self):
        """Test marking a payout as failed as admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('payout-fail', args=[self.rider_payout.payout_id])
        data = {'notes': 'Invalid account details'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rider_payout.refresh_from_db()
        self.assertEqual(self.rider_payout.status, 'failed')
        self.assertEqual(self.rider_payout.notes, 'Invalid account details')
    
    def test_stats_endpoint_as_admin(self):
        """Test the stats endpoint as admin"""
        # Create a processed payout
        Payout.objects.create(
            user=self.farmer,
            amount=Decimal('200.00'),
            status='processed',
            transaction_reference='TX987654321',
            processed_date=timezone.now()
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('payout-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_pending'], 2)
        self.assertEqual(response.data['total_processed'], 1)
        self.assertEqual(response.data['amount_pending'], Decimal('150.00'))
        self.assertEqual(response.data['amount_processed'], Decimal('200.00'))
    
    def test_stats_endpoint_as_farmer(self):
        """Test the stats endpoint as farmer"""
        # Create a processed payout for the farmer
        Payout.objects.create(
            user=self.farmer,
            amount=Decimal('200.00'),
            status='processed',
            transaction_reference='TX987654321',
            processed_date=timezone.now()
        )
        
        self.client.force_authenticate(user=self.farmer)
        url = reverse('payout-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_pending'], 1)  # Only the farmer's pending payout
        self.assertEqual(response.data['total_processed'], 1)  # Only the farmer's processed payout
        self.assertEqual(response.data['amount_pending'], Decimal('100.00'))
        self.assertEqual(response.data['amount_processed'], Decimal('200.00'))
