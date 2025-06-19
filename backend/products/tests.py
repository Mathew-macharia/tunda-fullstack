from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import ProductCategory, Product, ProductListing
from farms.models import Farm
from locations.models import Location

User = get_user_model()

class ProductCategoryModelTests(TestCase):
    def setUp(self):
        # Create a parent category
        self.parent_category = ProductCategory.objects.create(
            category_name="Vegetables",
            description="All types of vegetables"
        )
        
        # Create a child category
        self.child_category = ProductCategory.objects.create(
            parent_category=self.parent_category,
            category_name="Leafy Greens",
            description="Leafy green vegetables"
        )
    
    def test_category_creation(self):
        """Test creating a product category"""
        self.assertEqual(self.parent_category.category_name, "Vegetables")
        self.assertEqual(self.child_category.parent_category, self.parent_category)
        self.assertTrue(self.parent_category.is_active)
        
    def test_category_str_representation(self):
        """Test the string representation of a category"""
        self.assertEqual(str(self.parent_category), "Vegetables")
        
    def test_category_hierarchy(self):
        """Test the parent-child relationship between categories"""
        children = self.parent_category.children.all()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first(), self.child_category)

class ProductModelTests(TestCase):
    def setUp(self):
        # Create a category
        self.category = ProductCategory.objects.create(
            category_name="Fruits",
            description="All types of fruits"
        )
    
    def test_product_creation(self):
        """Test creating a product"""
        product = Product.objects.create(
            category=self.category,
            product_name="Apple",
            description="Fresh red apples",
            unit_of_measure="kg",
            is_perishable=True,
            shelf_life_days=14,
            image_url="http://example.com/apple.jpg"
        )
        
        self.assertEqual(product.product_name, "Apple")
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.unit_of_measure, "kg")
        self.assertTrue(product.is_perishable)
        self.assertEqual(product.shelf_life_days, 14)
        self.assertEqual(product.image_url, "http://example.com/apple.jpg")
        self.assertTrue(product.is_active)
        
    def test_product_str_representation(self):
        """Test the string representation of a product"""
        product = Product.objects.create(
            category=self.category,
            product_name="Banana",
            unit_of_measure="kg"
        )
        self.assertEqual(str(product), "Banana")

class ProductCategoryAPITests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_role="admin",
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            phone_number="0787654321",
            password="testpass456",
            first_name="Regular",
            last_name="User",
            user_role="customer"
        )
        
        # Create farmer user
        self.farmer_user = User.objects.create_user(
            phone_number="0723456789",
            password="testpass789",
            first_name="Farmer",
            last_name="User",
            user_role="farmer"
        )
        
        # Create a parent category
        self.parent_category = ProductCategory.objects.create(
            category_name="Vegetables",
            description="All types of vegetables"
        )
        
        # Create a child category
        self.child_category = ProductCategory.objects.create(
            parent_category=self.parent_category,
            category_name="Leafy Greens",
            description="Leafy green vegetables"
        )
        
        self.client = APIClient()
    
    def test_list_categories(self):
        """Test listing categories (should be accessible to all)"""
        url = reverse('productcategory-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two categories
    
    def test_create_category_as_admin(self):
        """Test creating a category as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('productcategory-list')
        data = {
            'category_name': 'Fruits',
            'description': 'All types of fruits',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 3)
        self.assertEqual(response.data['category_name'], 'Fruits')
    
    def test_create_category_as_regular_user(self):
        """Test creating a category as regular user (should fail)"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('productcategory-list')
        data = {
            'category_name': 'Fruits',
            'description': 'All types of fruits',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_category_as_admin(self):
        """Test updating a category as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('productcategory-detail', args=[self.parent_category.category_id])
        data = {'description': 'Updated description'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')
    
    def test_filter_root_categories(self):
        """Test filtering root categories"""
        url = reverse('productcategory-list') + '?parent_id=null'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One root category
        self.assertEqual(response.data[0]['category_name'], 'Vegetables')
    
    def test_filter_child_categories(self):
        """Test filtering child categories"""
        url = reverse('productcategory-list') + f'?parent_id={self.parent_category.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One child category
        self.assertEqual(response.data[0]['category_name'], 'Leafy Greens')
    
    def test_get_category_children(self):
        """Test getting children of a category"""
        url = reverse('productcategory-children', args=[self.parent_category.category_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One child
        self.assertEqual(response.data[0]['category_name'], 'Leafy Greens')

class ProductAPITests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            phone_number="0712345678",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_role="admin",
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            phone_number="0787654321",
            password="testpass456",
            first_name="Regular",
            last_name="User",
            user_role="customer"
        )
        
        # Create farmer user
        self.farmer_user = User.objects.create_user(
            phone_number="0723456789",
            password="testpass789",
            first_name="Farmer",
            last_name="User",
            user_role="farmer"
        )
        
        # Create categories
        self.vegetables_category = ProductCategory.objects.create(
            category_name="Vegetables",
            description="All types of vegetables"
        )
        
        self.fruits_category = ProductCategory.objects.create(
            category_name="Fruits",
            description="All types of fruits"
        )
        
        # Create products
        self.product1 = Product.objects.create(
            category=self.vegetables_category,
            product_name="Kale",
            description="Fresh green kale",
            unit_of_measure="bunch",
            is_perishable=True,
            shelf_life_days=5,
            image_url="http://example.com/kale.jpg"
        )
        
        self.product2 = Product.objects.create(
            category=self.fruits_category,
            product_name="Mango",
            description="Sweet ripe mangoes",
            unit_of_measure="kg",
            is_perishable=True,
            shelf_life_days=7,
            image_url="http://example.com/mango.jpg"
        )
        
        self.client = APIClient()
    
    def test_list_products(self):
        """Test listing products (should be accessible to all)"""
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two products
    
    def test_create_product_as_farmer(self):
        """Test creating a product as farmer"""
        self.client.force_authenticate(user=self.farmer_user)
        
        url = reverse('product-list')
        data = {
            'category': self.vegetables_category.category_id,
            'product_name': 'Spinach',
            'description': 'Fresh spinach leaves',
            'unit_of_measure': 'bunch',
            'is_perishable': True,
            'shelf_life_days': 4,
            'image_url': 'http://example.com/spinach.jpg'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(response.data['product_name'], 'Spinach')
    
    def test_create_product_as_regular_user(self):
        """Test creating a product as regular user (should fail)"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('product-list')
        data = {
            'category': self.vegetables_category.category_id,
            'product_name': 'Spinach',
            'description': 'Fresh spinach leaves',
            'unit_of_measure': 'bunch',
            'is_perishable': True,
            'shelf_life_days': 4,
            'image_url': 'http://example.com/spinach.jpg'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_product_as_admin(self):
        """Test updating a product as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('product-detail', args=[self.product1.product_id])
        data = {
            'description': 'Updated kale description',
            'shelf_life_days': 6
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated kale description')
        self.assertEqual(response.data['shelf_life_days'], 6)
    
    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        url = reverse('product-list') + f'?category_id={self.vegetables_category.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One product in vegetables category
        self.assertEqual(response.data[0]['product_name'], 'Kale')
    
class ProductListingAPITests(APITestCase):
    """Test the ProductListing API"""

    def setUp(self):
        # Create users
        self.admin_user = get_user_model().objects.create_user(
            phone_number='254700000001',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='testpass123',
            user_role='admin'
        )
        self.farmer_user = get_user_model().objects.create_user(
            phone_number='254700000002',
            email='farmer@example.com',
            first_name='Farmer',
            last_name='User',
            password='testpass123',
            user_role='farmer'
        )
        self.another_farmer = get_user_model().objects.create_user(
            phone_number='254700000003',
            email='farmer2@example.com',
            first_name='Another',
            last_name='Farmer',
            password='testpass123',
            user_role='farmer'
        )
        self.customer_user = get_user_model().objects.create_user(
            phone_number='254700000004',
            email='customer@example.com',
            first_name='Customer',
            last_name='User',
            password='testpass123',
            user_role='customer'
        )
        
        # Create locations
        self.farmer_location = Location.objects.create(
            user=self.farmer_user,
            location_name='Farm Location',
            sub_location='Sub Farm',
            landmark='Near River',
            latitude=1.23456,
            longitude=36.78901,
            is_default=True
        )
        
        # Create farms
        self.farm = Farm.objects.create(
            farmer=self.farmer_user,
            farm_name='Test Farm',
            farm_description='A test farm',
            total_acreage=5.0,
            location=self.farmer_location,
            is_certified_organic=True
        )
        
        # Create another farm for another farmer
        self.another_location = Location.objects.create(
            user=self.another_farmer,
            location_name='Another Location',
            sub_location='Sub Location',
            landmark='Near Hill',
            latitude=1.12345,
            longitude=36.67890,
            is_default=True
        )
        
        self.another_farm = Farm.objects.create(
            farmer=self.another_farmer,
            farm_name='Another Farm',
            farm_description='Another test farm',
            total_acreage=3.0,
            location=self.another_location,
            is_certified_organic=False
        )
        
        # Create categories
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
            notes='Fresh from the farm'
        )
    
    def test_create_product_listing_as_farmer(self):
        """Test creating a product listing as a farmer"""
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-list')
        data = {
            'farm': self.farm.farm_id,
            'product': self.mango_product.product_id,
            'current_price': 75.00,
            'quantity_available': 50.00,
            'min_order_quantity': 2.00,
            'expected_harvest_date': (timezone.now() + timezone.timedelta(days=3)).date().isoformat(),
            'quality_grade': 'standard',
            'listing_status': 'pre_order',
            'notes': 'Pre-order mangoes'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductListing.objects.count(), 2)  # Initial + new listing
        self.assertEqual(response.data['product_name'], 'Mango')
        self.assertEqual(response.data['farm_name'], 'Test Farm')
        self.assertEqual(response.data['listing_status'], 'pre_order')
        self.assertEqual(response.data['farmer'], self.farmer_user.user_id)  # Farmer ID should be set automatically
    
    def test_customer_cannot_create_listing(self):
        """Test that customers cannot create product listings"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-listing-list')
        data = {
            'farm': self.farm.farm_id,
            'product': self.mango_product.product_id,
            'current_price': 75.00,
            'quantity_available': 50.00,
            'min_order_quantity': 2.00,
            'harvest_date': timezone.now().date().isoformat(),
            'quality_grade': 'standard',
            'listing_status': 'available',
            'notes': 'Fresh mangoes'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProductListing.objects.count(), 1)  # Only the initial listing
    
    def test_farmer_cannot_use_another_farmers_farm(self):
        """Test that a farmer cannot create a listing for another farmer's farm"""
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-list')
        data = {
            'farm': self.another_farm.farm_id,  # Another farmer's farm
            'product': self.kale_product.product_id,
            'current_price': 60.00,
            'quantity_available': 40.00,
            'min_order_quantity': 1.00,
            'harvest_date': timezone.now().date().isoformat(),
            'quality_grade': 'standard',
            'listing_status': 'available',
            'notes': 'Fresh kale'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProductListing.objects.count(), 1)  # Only the initial listing
        self.assertIn('farm', response.data)  # Should have a validation error for farm
    
    def test_update_own_listing(self):
        """Test that a farmer can update their own listing"""
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-detail', args=[self.kale_listing.listing_id])
        data = {
            'current_price': 55.00,
            'quantity_available': 90.00,  # Add this to pass validation
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['current_price']), 55.00)
        self.assertEqual(response.data['notes'], 'Updated notes')
    
    def test_cannot_update_another_farmers_listing(self):
        """Test that a farmer cannot update another farmer's listing"""
        # Create a listing for another farmer
        another_listing = ProductListing.objects.create(
            farmer=self.another_farmer,
            farm=self.another_farm,
            product=self.mango_product,
            current_price=80.00,
            quantity_available=30.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='standard',
            is_organic_certified=False,
            listing_status='available',
            notes='Fresh mangoes'
        )
        
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-detail', args=[another_listing.listing_id])
        data = {
            'current_price': 75.00,
            'quantity_available': 25.00,  # Add this for validation
            'notes': 'Trying to update another farmer\'s listing'
        }
        response = self.client.patch(url, data, format='json')
        
        # Update the expected status to match what the view actually returns
        # This could be 404 if the view is checking permissions at the queryset level
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify the listing was not updated
        another_listing.refresh_from_db()
        self.assertEqual(float(another_listing.current_price), 80.00)
    
    def test_list_only_available_listings_for_customers(self):
        """Test that customers can only see available or pre_order listings"""
        # Create some listings with different statuses
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=70.00,
            quantity_available=20.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='premium',
            is_organic_certified=True,
            listing_status='sold_out',  # Should not be visible to customers
            notes='Sold out mangoes'
        )
        
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=65.00,
            quantity_available=15.00,
            min_order_quantity=1.00,
            expected_harvest_date=(timezone.now() + timezone.timedelta(days=5)).date(),
            quality_grade='standard',
            is_organic_certified=True,
            listing_status='pre_order',  # Should be visible to customers
            notes='Pre-order mangoes'
        )
        
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=60.00,
            quantity_available=25.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='economy',
            is_organic_certified=True,
            listing_status='inactive',  # Should not be visible to customers
            notes='Inactive mangoes'
        )
        
        # Test unauthenticated user view
        self.client.force_authenticate(user=None)
        url = reverse('product-listing-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only available and pre_order listings
        
        # Test customer view
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only available and pre_order listings
    
    def test_farmers_see_all_their_listings(self):
        """Test that farmers can see all their listings regardless of status"""
        # Create some listings with different statuses
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=70.00,
            quantity_available=20.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='premium',
            is_organic_certified=True,
            listing_status='sold_out',
            notes='Sold out mangoes'
        )
        
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=60.00,
            quantity_available=25.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='economy',
            is_organic_certified=True,
            listing_status='inactive',
            notes='Inactive mangoes'
        )
        
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All listings for this farmer
    
    def test_filter_listings(self):
        """Test filtering listings by various parameters"""
        # Create some more listings for filtering
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=90.00,
            quantity_available=10.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='premium',
            is_organic_certified=True,
            listing_status='available',
            notes='Premium mangoes'
        )
        
        # Test filtering by product_id
        self.client.force_authenticate(user=None)  # Unauthenticated user
        url = reverse('product-listing-list') + f'?product_id={self.mango_product.product_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only available mango listings
        self.assertEqual(response.data[0]['product_name'], 'Mango')
        
        # Test filtering by farm_id
        url = reverse('product-listing-list') + f'?farm_id={self.farm.farm_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # All available listings from the farm
        
        # Test filtering by quality_grade
        url = reverse('product-listing-list') + f'?quality=premium'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # All premium available listings
        
        # Test filtering by price range
        # Make sure we have a listing in this price range
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.kale_product,
            current_price=70.00,
            quantity_available=20.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='standard',
            is_organic_certified=False,
            listing_status='available',
            notes='Mid-price kale'
        )
        
        url = reverse('product-listing-list') + '?min_price=60&max_price=80'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only listings in this price range
        self.assertEqual(float(response.data[0]['current_price']), 70.00)
        
        # Test filtering by organic certification
        url = reverse('product-listing-list') + '?organic=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item['is_organic_certified'] for item in response.data))
    
    def test_mark_available(self):
        """Test marking a listing as available"""
        # First mark it as sold out
        self.kale_listing.listing_status = 'sold_out'
        self.kale_listing.harvest_date = None  # Clear harvest date to test auto-setting
        self.kale_listing.save()
        
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-mark-available', args=[self.kale_listing.listing_id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['listing_status'], 'available')
        
        # Refresh from database
        self.kale_listing.refresh_from_db()
        self.assertEqual(self.kale_listing.listing_status, 'available')
        
    def test_mark_pre_order(self):
        """Test marking a listing as pre-order"""
        # Set expected harvest date to satisfy validation
        self.kale_listing.expected_harvest_date = timezone.now().date() + timezone.timedelta(days=30)
        self.kale_listing.save()
        
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-mark-pre-order', args=[self.kale_listing.listing_id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['listing_status'], 'pre_order')
    
    def test_my_listings_endpoint(self):
        """Test the my_listings endpoint for farmers"""
        # Update the existing kale listing to sold_out to test filtering
        self.kale_listing.listing_status = 'sold_out'
        self.kale_listing.save()
        
        # Create a new listing for the farmer that's available
        ProductListing.objects.create(
            farmer=self.farmer_user,
            farm=self.farm,
            product=self.mango_product,
            current_price=85.00,
            quantity_available=15.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='standard',
            is_organic_certified=True,
            listing_status='available',
            notes='Standard mangoes'
        )
        
        # Create a listing for another farmer
        ProductListing.objects.create(
            farmer=self.another_farmer,
            farm=self.another_farm,
            product=self.kale_product,
            current_price=45.00,
            quantity_available=25.00,
            min_order_quantity=1.00,
            harvest_date=timezone.now().date(),
            quality_grade='standard',
            is_organic_certified=False,
            listing_status='available',
            notes='Another farmer\'s kale'
        )
        
        self.client.force_authenticate(user=self.farmer_user)
        url = reverse('product-listing-my-listings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only this farmer's listings
        self.assertTrue(all(item['farmer'] == self.farmer_user.user_id for item in response.data))
        
        # Test filtering by status
        url = reverse('product-listing-my-listings') + '?status=available'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only available listings
        self.assertEqual(response.data[0]['listing_status'], 'available')
        
        # Test that customers cannot access this endpoint
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-listing-my-listings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_perishable_products(self):
        """Test filtering perishable products"""
        # Create a non-perishable product
        Product.objects.create(
            category=self.fruits_category,
            product_name="Dried Mango",
            description="Dried mango pieces",
            unit_of_measure="kg",
            is_perishable=False,
            shelf_life_days=90,
            image_url="http://example.com/dried_mango.jpg"
        )
        
        url = reverse('product-perishable')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two perishable products
        
        # Ensure only perishable products are returned
        product_names = [product['product_name'] for product in response.data]
        self.assertIn('Kale', product_names)
        self.assertIn('Mango', product_names)
        self.assertNotIn('Dried Mango', product_names)
    
    def test_filter_non_perishable_products(self):
        """Test filtering non-perishable products"""
        # Create a non-perishable product
        Product.objects.create(
            category=self.fruits_category,
            product_name="Dried Mango",
            description="Dried mango pieces",
            unit_of_measure="kg",
            is_perishable=False,
            shelf_life_days=90,
            image_url="http://example.com/dried_mango.jpg"
        )
        
        url = reverse('product-non-perishable')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One non-perishable product
        self.assertEqual(response.data[0]['product_name'], 'Dried Mango')
