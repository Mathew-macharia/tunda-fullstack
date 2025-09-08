from django.test import TestCase
from unittest.mock import patch, MagicMock
from users.models import User
from orders.models import Order, OrderItem
from products.models import Product, ProductListing
from farms.models import Farm
from locations.models import Location
from communication.models import Notification
from communication.services import NotificationService
from communication.tasks import send_notification_task
from delivery.models import Delivery
from django.utils import timezone
import uuid
from decimal import Decimal

class NotificationSystemTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            phone_number='+254712345678',
            password='password123',
            first_name='John',
            last_name='Doe',
            user_role='customer',
            sms_notifications=True,
            order_updates=True
        )
        self.farmer = User.objects.create_user(
            phone_number='+254722334455',
            password='password123',
            first_name='Jane',
            last_name='Farmer',
            user_role='farmer',
            sms_notifications=True,
            order_updates=True
        )
        self.rider = User.objects.create_user(
            phone_number='+254733445566',
            password='password123',
            first_name='Mike',
            last_name='Rider',
            user_role='rider',
            sms_notifications=True,
            order_updates=True
        )
        self.admin_user = User.objects.create_superuser(
            phone_number='+254744556677',
            password='password123',
            first_name='Admin',
            last_name='User',
            user_role='admin',
            sms_notifications=True,
            order_updates=True, # Admins should receive system messages
            system_message=True # Ensure admin can receive system messages
        )

        self.location = Location.objects.create(
            location_name='Test Location',
            county='Test County',
            sub_county='Test Subcounty',
            latitude=1.0,
            longitude=36.0
        )
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name='Test Farm',
            location=self.location,
            contact_phone='+254700112233'
        )
        self.product = Product.objects.create(
            product_name='Test Product',
            description='A test product',
            unit_of_measure='kg'
        )
        self.listing = ProductListing.objects.create(
            product=self.product,
            farm=self.farm,
            price_per_unit=Decimal('100.00'),
            available_quantity=Decimal('10.00'),
            is_active=True
        )

    @patch('communication.tasks.send_notification_task.delay')
    def test_notification_service_dispatches_task(self, mock_delay):
        """
        Test that NotificationService.send_notification dispatches a Celery task.
        """
        NotificationService.send_notification(
            user=self.customer,
            notification_type='order_update',
            title='Test Title',
            message='Test Message',
            send_sms=True,
            related_id=uuid.uuid4()
        )

        mock_delay.assert_called_once()
        args, kwargs = mock_delay.call_args
        self.assertEqual(kwargs['user_id'], self.customer.user_id)
        self.assertEqual(kwargs['notification_type'], 'order_update')
        self.assertEqual(kwargs['title'], 'Test Title')
        self.assertEqual(kwargs['message'], 'Test Message')
        self.assertTrue(kwargs['send_sms'])
        self.assertIsInstance(uuid.UUID(kwargs['related_id']), uuid.UUID) # Check if it's a valid UUID string

    @patch('africastalking.SMS.send') # Mock the actual Africa's Talking send method
    def test_send_notification_task_creates_notification_and_sends_sms(self, mock_africastalking_send):
        """
        Test that the Celery task correctly creates a Notification and calls SMSService.send_sms,
        which in turn calls Africa's Talking.
        """
        # Configure mock response for Africa's Talking
        mock_africastalking_send.return_value = {
            'SMSMessageData': {
                'Message': 'Sent to 1/1 Total Cost: KES 0.8000',
                'Recipients': [{
                    'statusCode': 100,
                    'number': self.customer.phone_number,
                    'cost': 'KES 0.8000',
                    'status': 'Success',
                    'messageId': 'ATXid_...'
                }]
            }
        }

        initial_notification_count = Notification.objects.count()
        test_related_id = uuid.uuid4()

        send_notification_task(
            user_id=self.customer.user_id,
            notification_type='order_update',
            title='Task Test Title',
            message='Task Test Message',
            send_sms=True,
            related_id=str(test_related_id)
        )

        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)
        notification = Notification.objects.get(related_id=test_related_id)
        self.assertEqual(notification.user, self.customer)
        self.assertEqual(notification.notification_type, 'order_update')
        self.assertEqual(notification.title, 'Task Test Title')
        self.assertEqual(notification.message, 'Task Test Message')
        self.assertTrue(notification.send_sms) # Stored as True because user prefers SMS

        mock_africastalking_send.assert_called_once_with('Task Test Message', [self.customer.phone_number])

    @patch('africastalking.SMS.send') # Mock the actual Africa's Talking send method
    def test_send_notification_task_does_not_send_sms_if_user_opted_out(self, mock_africastalking_send):
        """
        Test that the Celery task does not send SMS if the user has opted out,
        even if send_sms=True is passed to the task.
        """
        self.customer.sms_notifications = False
        self.customer.save()

        initial_notification_count = Notification.objects.count()
        test_related_id = uuid.uuid4()

        send_notification_task(
            user_id=self.customer.user_id,
            notification_type='order_update',
            title='Task Test Title No SMS',
            message='Task Test Message No SMS',
            send_sms=True,
            related_id=str(test_related_id)
        )

        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)
        notification = Notification.objects.get(related_id=test_related_id)
        self.assertFalse(notification.send_sms) # Stored as False because user opted out

        mock_africastalking_send.assert_not_called()

    @patch('communication.services.NotificationService.send_notification')
    def test_order_creation_notifications(self, mock_send_notification):
        """
        Test that appropriate notifications are sent on order creation.
        """
        order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('150.00')
        )
        OrderItem.objects.create(
            order=order,
            listing=self.listing,
            farmer=self.farmer,
            quantity=Decimal('1.00'),
            price_at_purchase=Decimal('100.00'),
            total_price=Decimal('100.00')
        )

        # Expected calls: Customer, Farmer, Admin
        self.assertEqual(mock_send_notification.call_count, 3)

        # Check customer notification
        customer_call = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.customer),
            None
        )
        self.assertIsNotNone(customer_call)
        self.assertEqual(customer_call.kwargs['notification_type'], 'order_update')
        self.assertIn('Order Confirmed', customer_call.kwargs['title'])
        self.assertTrue(customer_call.kwargs['send_sms'])
        self.assertEqual(customer_call.kwargs['related_id'], order.order_id)

        # Check farmer notification
        farmer_call = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.farmer),
            None
        )
        self.assertIsNotNone(farmer_call)
        self.assertEqual(farmer_call.kwargs['notification_type'], 'order_update')
        self.assertIn('New Order Received', farmer_call.kwargs['title'])
        self.assertTrue(farmer_call.kwargs['send_sms'])
        self.assertEqual(farmer_call.kwargs['related_id'], order.order_id)

        # Check admin notification
        admin_call = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.admin_user),
            None
        )
        self.assertIsNotNone(admin_call)
        self.assertEqual(admin_call.kwargs['notification_type'], 'system_message')
        self.assertIn('New Order Placed', admin_call.kwargs['title'])
        self.assertTrue(admin_call.kwargs['send_sms'])
        self.assertEqual(admin_call.kwargs['related_id'], order.order_id)

    @patch('communication.services.NotificationService.send_notification')
    def test_order_status_change_notifications(self, mock_send_notification):
        """
        Test that appropriate notifications are sent when order status changes.
        """
        order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('150.00'),
            order_status='confirmed' # Start as confirmed
        )
        # Clear initial calls from creation
        mock_send_notification.reset_mock()

        # Change status to processing
        order.order_status = 'processing'
        order.save()
        
        customer_call_processing = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.customer and 'processing' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(customer_call_processing)
        self.assertEqual(customer_call_processing.kwargs['notification_type'], 'order_update')
        self.assertIn('Order Update', customer_call_processing.kwargs['title'])
        self.assertTrue(customer_call_processing.kwargs['send_sms'])
        self.assertEqual(customer_call_processing.kwargs['related_id'], order.order_id)
        mock_send_notification.reset_mock()

        # Change status to delivered
        order.order_status = 'delivered'
        order.save()

        # Expected calls: Customer, Admin
        self.assertEqual(mock_send_notification.call_count, 2)

        customer_call_delivered = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.customer and 'delivered successfully' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(customer_call_delivered)
        self.assertEqual(customer_call_delivered.kwargs['notification_type'], 'order_update')
        self.assertIn('Order Update', customer_call_delivered.kwargs['title'])
        self.assertTrue(customer_call_delivered.kwargs['send_sms'])
        self.assertEqual(customer_call_delivered.kwargs['related_id'], order.order_id)

        admin_call_delivered = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.admin_user and 'has been delivered' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(admin_call_delivered)
        self.assertEqual(admin_call_delivered.kwargs['notification_type'], 'system_message')
        self.assertIn('Order Status Alert', admin_call_delivered.kwargs['title'])
        self.assertTrue(admin_call_delivered.kwargs['send_sms'])
        self.assertEqual(admin_call_delivered.kwargs['related_id'], order.order_id)

    @patch('communication.services.NotificationService.send_notification')
    def test_delivery_status_change_notifications(self, mock_send_notification):
        """
        Test that appropriate notifications are sent when delivery status changes.
        """
        order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('150.00'),
            order_status='confirmed'
        )
        delivery = Delivery.objects.create(
            order=order,
            rider=self.rider,
            delivery_status='assigned'
        )
        # Clear initial calls from creation/assignment
        mock_send_notification.reset_mock()

        # Change delivery status to picked_up
        delivery.delivery_status = 'picked_up'
        delivery.save()

        # Expected calls: Rider, Admin
        self.assertEqual(mock_send_notification.call_count, 2)

        rider_call_picked_up = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.rider and 'picked up Order' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(rider_call_picked_up)
        self.assertEqual(rider_call_picked_up.kwargs['notification_type'], 'order_update')
        self.assertIn('Delivery Status', rider_call_picked_up.kwargs['title'])
        self.assertTrue(rider_call_picked_up.kwargs['send_sms'])
        self.assertEqual(rider_call_picked_up.kwargs['related_id'], delivery.delivery_id)

        admin_call_picked_up = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.admin_user and 'has picked up Order' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(admin_call_picked_up)
        self.assertEqual(admin_call_picked_up.kwargs['notification_type'], 'system_message')
        self.assertIn('Delivery Alert', admin_call_picked_up.kwargs['title'])
        self.assertTrue(admin_call_picked_up.kwargs['send_sms'])
        self.assertEqual(admin_call_picked_up.kwargs['related_id'], delivery.delivery_id)
        mock_send_notification.reset_mock()

        # Change delivery status to delivered
        delivery.delivery_status = 'delivered'
        delivery.save()

        # Expected calls: Rider, Admin
        self.assertEqual(mock_send_notification.call_count, 2)

        rider_call_delivered = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.rider and 'successfully delivered Order' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(rider_call_delivered)
        self.assertEqual(rider_call_delivered.kwargs['notification_type'], 'order_update')
        self.assertIn('Delivery Status', rider_call_delivered.kwargs['title'])
        self.assertTrue(rider_call_delivered.kwargs['send_sms'])
        self.assertEqual(rider_call_delivered.kwargs['related_id'], delivery.delivery_id)

        admin_call_delivered = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.admin_user and 'has been delivered by' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(admin_call_delivered)
        self.assertEqual(admin_call_delivered.kwargs['notification_type'], 'system_message')
        self.assertIn('Delivery Alert', admin_call_delivered.kwargs['title'])
        self.assertTrue(admin_call_delivered.kwargs['send_sms'])
        self.assertEqual(admin_call_delivered.kwargs['related_id'], delivery.delivery_id)

    @patch('communication.services.NotificationService.send_notification')
    def test_rider_assignment_notification(self, mock_send_notification):
        """
        Test that notifications are sent when a rider is assigned to a delivery.
        """
        order = Order.objects.create(
            customer=self.customer,
            delivery_location=self.location,
            total_amount=Decimal('150.00'),
            order_status='confirmed'
        )
        # Create delivery without rider initially
        delivery = Delivery.objects.create(
            order=order,
            delivery_status='pending_pickup'
        )
        mock_send_notification.reset_mock() # Clear calls from order creation

        # Assign rider
        delivery.rider = self.rider
        delivery.save()

        # Expected calls: Rider, Admin
        self.assertEqual(mock_send_notification.call_count, 2)

        rider_call = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.rider and 'assigned to deliver Order' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(rider_call)
        self.assertEqual(rider_call.kwargs['notification_type'], 'order_update')
        self.assertIn('Delivery Assignment', rider_call.kwargs['title'])
        self.assertTrue(rider_call.kwargs['send_sms'])
        self.assertEqual(rider_call.kwargs['related_id'], delivery.delivery_id)

        admin_call = next(
            (call for call in mock_send_notification.call_args_list if call.kwargs['user'] == self.admin_user and 'has been assigned to Order' in call.kwargs['message']),
            None
        )
        self.assertIsNotNone(admin_call)
        self.assertEqual(admin_call.kwargs['notification_type'], 'system_message')
        self.assertIn('Rider Assignment', admin_call.kwargs['title'])
        self.assertTrue(admin_call.kwargs['send_sms'])
        self.assertEqual(admin_call.kwargs['related_id'], delivery.delivery_id)
