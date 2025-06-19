"""
Management command to create sample data for the Tunda Soko marketplace.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from users.models import User
from locations.models import County, SubCounty, Location
from farms.models import Farm
from products.models import ProductCategory, Product, ProductListing

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample marketplace data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear existing data before creating samples',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Creating sample data...')
        
        # Create sample data
        counties = self.get_counties()
        locations = self.create_locations(counties)
        categories = self.create_categories()
        products = self.create_products(categories)
        farmers = self.create_farmers()
        customers = self.create_customers()
        farms = self.create_farms(farmers, locations)
        listings = self.create_product_listings(farms, products)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- Using {len(counties)} counties\n'
                f'- {len(locations)} sample locations\n'
                f'- {len(categories)} categories\n'
                f'- {len(products)} products\n'
                f'- {len(farmers)} farmers\n'
                f'- {len(customers)} customers\n'
                f'- {len(farms)} farms\n'
                f'- {len(listings)} product listings'
            )
        )

    def clear_data(self):
        """Clear existing sample data"""
        ProductListing.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Farm.objects.all().delete()
        Location.objects.filter(user__user_role__in=['farmer', 'admin']).delete()
        User.objects.filter(user_role__in=['farmer', 'customer']).delete()

    def get_counties(self):
        """Get existing counties from database"""
        counties = list(County.objects.all())
        if not counties:
            self.stdout.write(
                self.style.WARNING(
                    'No counties found! Please run: python manage.py populate_locations'
                )
            )
        return counties

    def create_locations(self, counties):
        """Create sample locations using the old Location model"""
        # Create admin user for locations
        admin_user, created = User.objects.get_or_create(
            phone_number='0700000000',
            defaults={
                'user_role': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@tundasoko.com',
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        locations = []
        for county in counties:
            sub_counties = list(county.sub_counties.all())
            for sub_county in sub_counties[:2]:  # Take first 2 sub-counties per county
                location, created = Location.objects.get_or_create(
                    location_name=sub_county.sub_county_name,
                    user=admin_user,
                    defaults={
                        'sub_location': f'{sub_county.sub_county_name}, {county.county_name}',
                        'landmark': f'Near {sub_county.sub_county_name} market',
                        'latitude': Decimal(str(round(random.uniform(-1.5, 1.0), 6))),
                        'longitude': Decimal(str(round(random.uniform(34.0, 41.0), 6))),
                    }
                )
                if created:
                    self.stdout.write(f'Created location: {location.location_name}')
                locations.append(location)
        
        return locations

    def create_categories(self):
        """Create product categories"""
        categories_data = [
            {'category_name': 'Vegetables', 'description': 'Fresh leafy greens and vegetables'},
            {'category_name': 'Fruits', 'description': 'Fresh seasonal fruits'},
            {'category_name': 'Herbs', 'description': 'Fresh herbs and spices'},
            {'category_name': 'Grains', 'description': 'Cereals and grain products'},
            {'category_name': 'Legumes', 'description': 'Beans, peas, and legumes'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                category_name=cat_data['category_name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.category_name}')
            categories.append(category)
        
        return categories

    def create_products(self, categories):
        """Create sample products"""
        products_data = {
            'Vegetables': [
                {'product_name': 'Fresh Tomatoes', 'unit_of_measure': 'kg', 'shelf_life_days': 7},
                {'product_name': 'Organic Spinach', 'unit_of_measure': 'bunch', 'shelf_life_days': 3},
                {'product_name': 'Green Peppers', 'unit_of_measure': 'kg', 'shelf_life_days': 10},
                {'product_name': 'Fresh Kales', 'unit_of_measure': 'bunch', 'shelf_life_days': 5},
                {'product_name': 'Carrots', 'unit_of_measure': 'kg', 'shelf_life_days': 14},
            ],
            'Fruits': [
                {'product_name': 'Sweet Bananas', 'unit_of_measure': 'bunch', 'shelf_life_days': 5},
                {'product_name': 'Fresh Mangoes', 'unit_of_measure': 'piece', 'shelf_life_days': 7},
                {'product_name': 'Passion Fruits', 'unit_of_measure': 'kg', 'shelf_life_days': 10},
                {'product_name': 'Avocados', 'unit_of_measure': 'piece', 'shelf_life_days': 7},
            ],
            'Herbs': [
                {'product_name': 'Fresh Coriander', 'unit_of_measure': 'bunch', 'shelf_life_days': 5},
                {'product_name': 'Mint Leaves', 'unit_of_measure': 'bunch', 'shelf_life_days': 3},
                {'product_name': 'Rosemary', 'unit_of_measure': 'bunch', 'shelf_life_days': 7},
            ],
            'Grains': [
                {'product_name': 'Maize', 'unit_of_measure': 'kg', 'shelf_life_days': 365, 'is_perishable': False},
                {'product_name': 'Rice', 'unit_of_measure': 'kg', 'shelf_life_days': 365, 'is_perishable': False},
            ],
            'Legumes': [
                {'product_name': 'Green Beans', 'unit_of_measure': 'kg', 'shelf_life_days': 7},
                {'product_name': 'Peas', 'unit_of_measure': 'kg', 'shelf_life_days': 5},
            ]
        }
        
        products = []
        for category in categories:
            if category.category_name in products_data:
                for prod_data in products_data[category.category_name]:
                    product, created = Product.objects.get_or_create(
                        product_name=prod_data['product_name'],
                        category=category,
                        defaults={
                            'unit_of_measure': prod_data['unit_of_measure'],
                            'shelf_life_days': prod_data['shelf_life_days'],
                            'is_perishable': prod_data.get('is_perishable', True),
                            'description': f'Fresh {prod_data["product_name"].lower()} from local farmers'
                        }
                    )
                    if created:
                        self.stdout.write(f'Created product: {product.product_name}')
                    products.append(product)
        
        return products

    def create_farmers(self):
        """Create sample farmers"""
        farmers_data = [
            {'phone_number': '0712345001', 'first_name': 'John', 'last_name': 'Mwangi', 'email': 'john.mwangi@example.com'},
            {'phone_number': '0712345002', 'first_name': 'Mary', 'last_name': 'Njoki', 'email': 'mary.njoki@example.com'},
            {'phone_number': '0712345003', 'first_name': 'Peter', 'last_name': 'Kamau', 'email': 'peter.kamau@example.com'},
            {'phone_number': '0712345004', 'first_name': 'Grace', 'last_name': 'Wanjiku', 'email': 'grace.wanjiku@example.com'},
            {'phone_number': '0712345005', 'first_name': 'David', 'last_name': 'Kiprotich', 'email': 'david.kiprotich@example.com'},
        ]
        
        farmers = []
        for farmer_data in farmers_data:
            farmer, created = User.objects.get_or_create(
                phone_number=farmer_data['phone_number'],
                defaults={
                    'user_role': 'farmer',
                    'first_name': farmer_data['first_name'],
                    'last_name': farmer_data['last_name'],
                    'email': farmer_data['email'],
                    'is_verified': True,
                }
            )
            if created:
                farmer.set_password('password123')
                farmer.save()
                self.stdout.write(f'Created farmer: {farmer.first_name} {farmer.last_name}')
            farmers.append(farmer)
        
        return farmers

    def create_customers(self):
        """Create sample customers"""
        customers_data = [
            {'phone_number': '0712346001', 'first_name': 'Sarah', 'last_name': 'Wanjiku', 'email': 'sarah.wanjiku@example.com'},
            {'phone_number': '0712346002', 'first_name': 'James', 'last_name': 'Ochieng', 'email': 'james.ochieng@example.com'},
        ]
        
        customers = []
        for customer_data in customers_data:
            customer, created = User.objects.get_or_create(
                phone_number=customer_data['phone_number'],
                defaults={
                    'user_role': 'customer',
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name'],
                    'email': customer_data['email'],
                    'is_verified': True,
                }
            )
            if created:
                customer.set_password('password123')
                customer.save()
                self.stdout.write(f'Created customer: {customer.first_name} {customer.last_name}')
            customers.append(customer)
        
        return customers

    def create_farms(self, farmers, locations):
        """Create sample farms"""
        farm_names = [
            'Green Valley Farm',
            'Sunrise Orchards',
            'Eco Fresh Farms',
            'Highland Gardens',
            'Organic Meadows',
        ]
        
        farms = []
        for i, farmer in enumerate(farmers):
            farm, created = Farm.objects.get_or_create(
                farmer=farmer,
                defaults={
                    'farm_name': farm_names[i],
                    'location': random.choice(locations),
                    'total_acreage': Decimal(str(random.uniform(1.0, 50.0))),
                    'farm_description': f'A sustainable farm specializing in fresh produce',
                    'is_certified_organic': random.choice([True, False]),
                    'weather_zone': random.choice(['highland', 'midland', 'lowland']),
                }
            )
            if created:
                self.stdout.write(f'Created farm: {farm.farm_name}')
            farms.append(farm)
        
        return farms

    def create_product_listings(self, farms, products):
        """Create sample product listings"""
        listings = []
        
        for farm in farms:
            # Each farm will have 3-5 product listings
            num_listings = random.randint(3, 5)
            farm_products = random.sample(products, min(num_listings, len(products)))
            
            for product in farm_products:
                # Random price based on product type
                base_prices = {
                    'kg': random.uniform(80, 200),
                    'bunch': random.uniform(30, 80),
                    'piece': random.uniform(20, 50),
                }
                
                base_price = base_prices.get(product.unit_of_measure, 100)
                
                listing, created = ProductListing.objects.get_or_create(
                    farmer=farm.farmer,
                    farm=farm,
                    product=product,
                    defaults={
                        'current_price': Decimal(str(round(base_price, 2))),
                        'quantity_available': Decimal(str(random.uniform(5, 100))),
                        'min_order_quantity': Decimal('1.0'),
                        'harvest_date': timezone.now().date() - timedelta(days=random.randint(0, 7)),
                        'quality_grade': random.choice(['premium', 'standard', 'economy']),
                        'is_organic_certified': farm.is_certified_organic,
                        'listing_status': random.choice(['available', 'available', 'available', 'pre_order']),
                        'notes': f'Fresh {product.product_name.lower()} from {farm.farm_name}',
                    }
                )
                if created:
                    self.stdout.write(f'Created listing: {product.product_name} from {farm.farm_name}')
                listings.append(listing)
        
        return listings 