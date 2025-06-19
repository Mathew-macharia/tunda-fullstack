from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from communication.models import Notification, Message, SupportTicket
from users.models import User
from orders.models import Order
from locations.models import Location
from payments.models import PaymentMethod
import uuid

class NotificationModelTestCase(TestCase):
    """Test case for the Notification model"""
    
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            user=self.customer,
            notification_type='order',
            title='Order Update',
            message='Your order has been shipped',
            is_read=False
        )
        
        self.assertEqual(notification.user, self.customer)
        self.assertEqual(notification.notification_type, 'order')
        self.assertEqual(notification.title, 'Order Update')
        self.assertEqual(notification.message, 'Your order has been shipped')
        self.assertEqual(notification.is_read, False)
    
    def test_notification_string_representation(self):
        """Test the string representation of a notification"""
        notification = Notification.objects.create(
            user=self.customer,
            notification_type='system',
            title='System Update',
            message='System maintenance scheduled'
        )
        
        expected_str = f"System Update - {self.customer.phone_number}"
        self.assertEqual(str(notification), expected_str)


class MessageModelTestCase(TestCase):
    """Test case for the Message model"""
    
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        self.farmer = User.objects.create_user(
            phone_number='+3456789012',
            email='farmer@example.com',
            first_name='Farmer',
            last_name='User',
            password='password',
            user_role='farmer'
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
    
    def test_create_message(self):
        """Test creating a message"""
        message = Message.objects.create(
            sender=self.customer,
            recipient=self.farmer,
            message_text='When will my order be ready?',
            order=self.order,
            message_type='text'
        )
        
        self.assertEqual(message.sender, self.customer)
        self.assertEqual(message.recipient, self.farmer)
        self.assertEqual(message.message_text, 'When will my order be ready?')
        self.assertEqual(message.message_type, 'text')
        self.assertEqual(message.order, self.order)
        self.assertEqual(message.is_read, False)
    
    def test_message_string_representation(self):
        """Test the string representation of a message"""
        message = Message.objects.create(
            sender=self.farmer,
            recipient=self.customer,
            message_text='Do you have fresh tomatoes?',
            message_type='text'
        )
        
        expected_str = f"Message from {self.farmer.phone_number} to {self.customer.phone_number}"
        self.assertEqual(str(message), expected_str)


class SupportTicketModelTestCase(TestCase):
    """Test case for the SupportTicket model"""
    
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
    
    def test_create_support_ticket(self):
        """Test creating a support ticket"""
        ticket = SupportTicket.objects.create(
            user=self.customer,
            subject='Payment Issue',
            description='My payment was processed but order shows unpaid',
            priority='high',
            status='open'
        )
        
        self.assertEqual(ticket.user, self.customer)
        self.assertEqual(ticket.subject, 'Payment Issue')
        self.assertEqual(ticket.description, 'My payment was processed but order shows unpaid')
        self.assertEqual(ticket.priority, 'high')
        self.assertEqual(ticket.status, 'open')
        self.assertIsNotNone(ticket.ticket_number)
        self.assertIsNone(ticket.resolved_at)
    
    def test_ticket_auto_generation(self):
        """Test ticket number auto generation"""
        ticket1 = SupportTicket.objects.create(
            user=self.customer,
            subject='Payment Issue',
            description='Payment problem'
        )
        
        ticket2 = SupportTicket.objects.create(
            user=self.customer,
            subject='Delivery Issue',
            description='Delivery problem'
        )
        
        self.assertIsNotNone(ticket1.ticket_number)
        self.assertIsNotNone(ticket2.ticket_number)
        self.assertNotEqual(ticket1.ticket_number, ticket2.ticket_number)
    
    def test_resolved_at_timestamp(self):
        """Test that resolved_at is set when status changes to resolved"""
        ticket = SupportTicket.objects.create(
            user=self.customer,
            subject='Payment Issue',
            description='Payment problem',
            status='open'
        )
        
        self.assertIsNone(ticket.resolved_at)
        
        ticket.status = 'resolved'
        ticket.save()
        
        self.assertIsNotNone(ticket.resolved_at)


class NotificationAPITestCase(APITestCase):
    """Test case for the Notification API endpoints"""
    
    def setUp(self):
        # Create test client
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        # Create test notifications
        self.notification1 = Notification.objects.create(
            user=self.customer,
            notification_type='order',
            title='Order Update',
            message='Your order has been shipped'
        )
        
        self.notification2 = Notification.objects.create(
            user=self.admin,
            notification_type='system',
            title='System Update',
            message='System maintenance scheduled'
        )
    
    def test_list_notifications(self):
        """Test listing notifications for a user"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Order Update')
    
    def test_mark_notification_read(self):
        """Test marking a notification as read"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('notification-mark-read', args=[self.notification1.notification_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)


class MessageAPITestCase(APITestCase):
    """Test case for the Message API endpoints"""
    
    def setUp(self):
        # Create test client
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        self.farmer = User.objects.create_user(
            phone_number='+3456789012',
            email='farmer@example.com',
            first_name='Farmer',
            last_name='User',
            password='password',
            user_role='farmer'
        )
        
        # Create test messages
        self.message1 = Message.objects.create(
            sender=self.customer,
            recipient=self.farmer,
            message_text='When will my order be delivered?',
            message_type='text'
        )
        
        self.message2 = Message.objects.create(
            sender=self.farmer,
            recipient=self.customer,
            message_text='Your order will be delivered tomorrow',
            message_type='text'
        )
    
    def test_inbox_endpoint(self):
        """Test the inbox endpoint"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('message-inbox')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message_text'], 'Your order will be delivered tomorrow')
    
    def test_sent_endpoint(self):
        """Test the sent endpoint"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('message-sent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message_text'], 'When will my order be delivered?')
    
    def test_send_message(self):
        """Test sending a message"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('message-list')
        data = {
            'recipient': self.farmer.user_id,
            'message_text': 'Do you deliver to my area?',
            'message_type': 'text'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_text'], 'Do you deliver to my area?')
        self.assertEqual(Message.objects.count(), 3)


class SupportTicketAPITestCase(APITestCase):
    """Test case for the SupportTicket API endpoints"""
    
    def setUp(self):
        # Create test client
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_user(
            phone_number='+1234567890',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password',
            user_role='admin'
        )
        
        self.customer = User.objects.create_user(
            phone_number='+2345678901',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='password',
            user_role='customer'
        )
        
        # Create test tickets
        self.ticket = SupportTicket.objects.create(
            user=self.customer,
            subject='Payment Issue',
            description='My payment was processed but order shows unpaid',
            priority='high',
            status='open'
        )
    
    def test_create_ticket(self):
        """Test creating a support ticket"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('support-ticket-list')
        data = {
            'subject': 'Delivery Issue',
            'description': 'My order is showing delivered but I have not received it',
            'priority': 'high',
            'category': 'delivery_issue',
            'user': str(self.customer.user_id)  # Add the user ID explicitly
        }
        # Print the request data for debugging
        print(f"Request data: {data}")
        response = self.client.post(url, data)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], 'Delivery Issue')
        self.assertEqual(SupportTicket.objects.count(), 2)
    
    def test_list_user_tickets(self):
        """Test listing tickets for a user"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('support-ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], 'Payment Issue')
    
    def test_admin_assign_ticket(self):
        """Test admin assigning a ticket"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('support-ticket-assign', args=[self.ticket.ticket_id])
        data = {'assigned_to': self.admin.user_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.admin)
