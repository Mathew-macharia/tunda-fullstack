from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from feedback.models import Review
from users.models import User
from orders.models import Order, OrderItem
from products.models import Product, ProductCategory, ProductListing, ProductCategory
from locations.models import Location
from payments.models import PaymentMethod
from farms.models import Farm
import uuid

class ReviewModelTestCase(TestCase):
    """Test case for the Review model"""
    
    def setUp(self):
        """Set up test data"""
        # Import UUID for testing
        import uuid
        
        # Create a fixed test UUID for consistent testing
        self.test_uuid = uuid.uuid4()
        
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
        
        # Create test farm
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name='Test Farm',
            farm_description='Test Farm Description',
            location=self.location
        )
        
        # Create test product category
        self.category = ProductCategory.objects.create(
            category_name='Test Category',
            description='Test Category Description'
        )
        
        # Create test product
        self.product = Product.objects.create(
            product_name='Test Product',
            description='Test Description',
            category=self.category,
            is_perishable=True,
            unit_of_measure='kg'
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
        
        # Create test product listing
        self.product_listing = ProductListing.objects.create(
            farmer=self.farmer,
            farm=self.farm,
            product=self.product,
            current_price=Decimal('10.00'),
            quantity_available=Decimal('50.00'),
            min_order_quantity=Decimal('1.0'),
            quality_grade='standard',
            listing_status='available'
        )
        
        # Create test order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            listing=self.product_listing,
            farmer=self.farmer,
            quantity=Decimal('5.00'),
            price_at_purchase=Decimal('10.00'),
            total_price=Decimal('50.00'),
            item_status='delivered'
        )
    
    def test_create_product_review(self):
        """Test creating a product review"""
        review = Review.objects.create(
            reviewer=self.customer,
            order_item=self.order_item,
            target_type='product',
            target_id=self.product.product_id,
            rating=Decimal('4.5'),
            comment='Great product!'
        )
        
        self.assertEqual(review.rating, Decimal('4.5'))
        self.assertEqual(review.comment, 'Great product!')
        self.assertEqual(review.target_type, 'product')
        self.assertEqual(review.target_id, self.product.product_id)
        self.assertEqual(review.is_verified_purchase, True)
    
    def test_review_string_representation(self):
        """Test the string representation of a review"""
        review = Review.objects.create(
            reviewer=self.customer,
            target_type='farmer',
            target_id=self.farmer.user_id,
            rating=Decimal('5.0'),
            comment='Excellent farmer!'
        )
        
        expected_str = f"{self.customer.phone_number}'s 5.0 star review of farmer"
        self.assertEqual(str(review), expected_str)


class ReviewAPITestCase(APITestCase):
    """Test case for the Review API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Import UUID for testing
        import uuid
        
        # Create a fixed test UUID for consistent testing
        self.test_uuid = uuid.uuid4()
        
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
        
        # Create test location
        self.location = Location.objects.create(
            user=self.customer,
            location_name='Test Location',
            latitude=0.0,
            longitude=0.0,
            landmark='Test Landmark',
            is_default=True
        )
        
        # Create test farm
        self.farm = Farm.objects.create(
            farmer=self.farmer,
            farm_name='Test Farm',
            farm_description='Test Farm Description',
            location=self.location
        )
        
        # Create test product category
        self.category = ProductCategory.objects.create(
            category_name='Test Category',
            description='Test Category Description'
        )
        
        # Create test product
        self.product = Product.objects.create(
            product_name='Test Product',
            description='Test Description',
            category=self.category,
            is_perishable=True,
            unit_of_measure='kg'
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
        
        # Create test product listing
        self.product_listing = ProductListing.objects.create(
            farmer=self.farmer,
            farm=self.farm,
            product=self.product,
            current_price=Decimal('10.00'),
            quantity_available=Decimal('50.00'),
            min_order_quantity=Decimal('1.0'),
            quality_grade='standard',
            listing_status='available'
        )
        
        # Create test order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            listing=self.product_listing,
            farmer=self.farmer,
            quantity=Decimal('5.00'),
            price_at_purchase=Decimal('10.00'),
            total_price=Decimal('50.00'),
            item_status='delivered'
        )
        
        # Create test review
        self.review = Review.objects.create(
            reviewer=self.customer,
            order_item=self.order_item,
            target_type='product',
            target_id=self.product.product_id,
            rating=Decimal('4.0'),
            comment='Good product'
        )
    
    def test_list_reviews(self):
        """Test listing reviews"""
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_review(self):
        """Test creating a review"""
        # Make sure the order is delivered to pass validation
        self.order.order_status = 'delivered'
        self.order.save()
        
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-list')
        data = {
            'order_item': self.order_item.order_item_id,
            'target_type': 'farmer',
            'target_id': str(self.test_uuid),  # Use our test UUID for consistency
            'rating': '5.0',
            'comment': 'Great farmer!'
        }
        
        # Print debugging information
        print(f"Test create review data: {data}")
        response = self.client.post(url, data)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data if response.status_code != 400 else response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment'], 'Great farmer!')
        self.assertEqual(Review.objects.count(), 2)
    
    def test_filter_reviews_by_target(self):
        """Test filtering reviews by target type and ID"""
        # Create a review for the product first to have something to filter
        self.order.order_status = 'delivered'
        self.order.save()
        
        # Create a product review first
        Review.objects.create(
            reviewer=self.customer,
            order_item=self.order_item,
            target_type='product',
            target_id=self.test_uuid,  # Use our test UUID for consistency
            rating=Decimal('4.5')
        )
        
        # Authenticate the user before making the request
        self.client.force_authenticate(user=self.customer)
        
        url = reverse('review-list')
        # Use the same test UUID we used to create the review
        query_params = {'target_type': 'product', 'target_id': str(self.test_uuid)}
        
        # Print debugging information
        print(f"Filter reviews query params: {query_params}")
        response = self.client.get(url, query_params)
        print(f"Filter response status: {response.status_code}")
        print(f"Filter response data: {response.content if response.status_code != 200 else response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_update_review(self):
        """Test updating a review by its owner"""
        self.client.force_authenticate(user=self.customer)
        url = reverse('review-detail', args=[self.review.review_id])
        data = {'rating': '3.5', 'comment': 'Updated comment'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], '3.5')
        self.assertEqual(response.data['comment'], 'Updated comment')
    
    def test_moderate_review(self):
        """Test moderating a review (admin only)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('review-moderate', args=[self.review.review_id])
        data = {'is_visible': False}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_visible'], False)
        
        # Regular users shouldn't be able to moderate
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(url, {'is_visible': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
