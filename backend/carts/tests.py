from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from products.models import ProductCategory, Product, ProductListing
from locations.models import Location
from farms.models import Farm
from .models import Cart, CartItem

User = get_user_model()

class CartAPITests(APITestCase):
    """Test cases for the Cart API"""
    
    def setUp(self):
        # Create test users with different roles
        self.customer_user = User.objects.create_user(
            phone_number='1234567890',
            password='testpassword',
            first_name='Customer',
            last_name='User',
            user_role='customer'
        )
        
        self.farmer_user = User.objects.create_user(
            phone_number='0987654321',
            password='testpassword',
            first_name='Farmer',
            last_name='User',
            user_role='farmer'
        )
        
        # Create a location
        self.location = Location.objects.create(
            user=self.farmer_user,
            location_name='Test Location',
            latitude=0.0,
            longitude=0.0,
            sub_location='Test Sub-Location',
            landmark='Test Landmark',
            is_default=True
        )
        
        # Create a farm
        self.farm = Farm.objects.create(
            farmer=self.farmer_user,
            farm_name='Test Farm',
            farm_description='A test farm',
            location=self.location,
            total_acreage=10.5
        )
        
        # Create product categories
        self.vegetables_category = ProductCategory.objects.create(
            category_name='Vegetables',
            description='Fresh vegetables'
        )
        
        self.fruits_category = ProductCategory.objects.create(
            category_name='Fruits',
            description='Fresh fruits'
        )
        
        # Create products
        self.kale_product = Product.objects.create(
            category=self.vegetables_category,
            product_name='Kale',
            description='Fresh kale',
            unit_of_measure='kg',
            is_perishable=True,
            shelf_life_days=7
        )
        
        self.mango_product = Product.objects.create(
            category=self.fruits_category,
            product_name='Mango',
            description='Sweet mangoes',
            unit_of_measure='kg',
            is_perishable=True,
            shelf_life_days=14
        )
        
        # Create product listings
        self.kale_listing = ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.kale_product,
            current_price=50.00,
            quantity_available=100.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='premium',
            is_organic_certified=True,
            listing_status='available',
            notes='Fresh premium kale'
        )
        
        self.mango_listing = ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=75.00,
            quantity_available=50.00,
            min_order_quantity=2.00,
            harvest_date=timezone.now().date(),
            quality_grade='premium',
            is_organic_certified=True,
            listing_status='available',
            notes='Fresh premium mangoes'
        )
        
        # Set up the API client
        self.client = APIClient()
        
    def test_cart_access_permissions(self):
        """Test that only customers can access carts"""
        # Unauthenticated user cannot access cart
        response = self.client.get(reverse('cart-my-cart'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Farmer cannot access cart
        self.client.force_authenticate(user=self.farmer_user)
        response = self.client.get(reverse('cart-my-cart'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Customer can access cart
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(reverse('cart-my-cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_or_create_cart(self):
        """Test getting or creating a cart for a customer"""
        self.client.force_authenticate(user=self.customer_user)
        
        # First request should create a new cart
        response = self.client.get(reverse('cart-my-cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer'], self.customer_user.user_id)
        self.assertEqual(len(response.data['items']), 0)
        
        # Subsequent requests should return the same cart
        cart_id = response.data['cart_id']
        response = self.client.get(reverse('cart-my-cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart_id'], cart_id)
        
    def test_add_item_to_cart(self):
        """Test adding an item to the cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Add kale to cart
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 5.0
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['listing'], self.kale_listing.listing_id)
        self.assertEqual(float(response.data['items'][0]['quantity']), 5.0)
        self.assertEqual(float(response.data['items'][0]['price_at_addition']), 50.0)
        self.assertEqual(float(response.data['total_items']), 5.0)
        self.assertEqual(float(response.data['total_cost']), 250.0)
        
    def test_update_cart_item_quantity(self):
        """Test updating the quantity of an item in the cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # First add an item to the cart
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 3.0
            },
            format='json'
        )
        
        cart_item_id = response.data['items'][0]['cart_item_id']
        
        # Update the quantity
        response = self.client.post(
            reverse('cart-update-quantity'),
            {
                'cart_item_id': cart_item_id,
                'quantity': 10.0
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['items'][0]['quantity']), 10.0)
        self.assertEqual(float(response.data['total_items']), 10.0)
        self.assertEqual(float(response.data['total_cost']), 500.0)
        
    def test_remove_item_from_cart(self):
        """Test removing an item from the cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # First add items to the cart
        self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 3.0
            },
            format='json'
        )
        
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.mango_listing.listing_id,
                'quantity': 4.0
            },
            format='json'
        )
        
        self.assertEqual(len(response.data['items']), 2)
        
        # Get the cart item ID for the first item
        cart_item_id = response.data['items'][0]['cart_item_id']
        
        # Remove the item
        response = self.client.post(
            reverse('cart-remove-item'),
            {
                'cart_item_id': cart_item_id
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        
    def test_clear_cart(self):
        """Test clearing all items from the cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Add items to the cart
        self.client.post(
            reverse('cart-add-item'),
            {'listing_id': self.kale_listing.listing_id, 'quantity': 3.0},
            format='json'
        )
        
        self.client.post(
            reverse('cart-add-item'),
            {'listing_id': self.mango_listing.listing_id, 'quantity': 4.0},
            format='json'
        )
        
        # Clear the cart
        response = self.client.post(reverse('cart-clear-cart'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)
        self.assertEqual(float(response.data['total_items']), 0.0)
        self.assertEqual(float(response.data['total_cost']), 0.0)
        
    def test_validation_quantity_exceeds_available(self):
        """Test validation when quantity exceeds available stock"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Try to add more than available
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 200.0  # More than the 100 available
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        
    def test_validation_min_order_quantity(self):
        """Test validation for minimum order quantity"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Try to add less than minimum order quantity
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.mango_listing.listing_id,
                'quantity': 1.0  # Less than the 2.0 minimum
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        
    def test_price_locking(self):
        """Test that price is locked at the time of adding to cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Add item to cart
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 5.0
            },
            format='json'
        )
        
        initial_price = float(response.data['items'][0]['price_at_addition'])
        self.assertEqual(initial_price, 50.0)
        
        # Change the price in the listing
        self.kale_listing.current_price = 60.0
        self.kale_listing.save()
        
        # Get the cart again
        response = self.client.get(reverse('cart-my-cart'))
        
        # Price in cart should still be the original price
        self.assertEqual(float(response.data['items'][0]['price_at_addition']), 50.0)
        
    def test_cannot_add_unavailable_listing(self):
        """Test that only available or pre-order listings can be added to cart"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Change listing status to sold_out
        self.kale_listing.listing_status = 'sold_out'
        self.kale_listing.save()
        
        # Try to add to cart
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 5.0
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Change to inactive
        self.kale_listing.listing_status = 'inactive'
        self.kale_listing.save()
        
        # Try to add to cart
        response = self.client.post(
            reverse('cart-add-item'),
            {
                'listing_id': self.kale_listing.listing_id,
                'quantity': 5.0
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
