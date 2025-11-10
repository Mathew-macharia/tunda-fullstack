from django.db import models
from django.conf import settings
from farms.models import Farm
from django.db.models import Avg, Count

class ProductCategory(models.Model):
    """Model representing product categories with hierarchical structure"""
    category_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='children',
        null=True, 
        blank=True
    )
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Product_Categories'
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return self.category_name

class Product(models.Model):
    """Model representing general product information"""
    UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('piece', 'Piece'),
        ('bunch', 'Bunch'),
        ('litre', 'Litre'),
        ('bag', 'Bag'),
    )
    
    product_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit_of_measure = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    is_perishable = models.BooleanField(default=True)
    shelf_life_days = models.IntegerField(default=7)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_perishable']),
        ]
    
    def __str__(self):
        return self.product_name
    
    @property
    def average_rating(self):
        """Get average rating from reviews (integrated after feedback app)"""
        try:
            from feedback.models import Review
            reviews = Review.objects.filter(
                target_type='product',
                target_id=str(self.product_id),
                is_visible=True
            )
            return reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        except ImportError:
            return 0
    
    @property
    def review_count(self):
        """Get total number of reviews (integrated after feedback app)"""
        try:
            from feedback.models import Review
            return Review.objects.filter(
                target_type='product',
                target_id=str(self.product_id),
                is_visible=True
            ).count()
        except ImportError:
            return 0
    
    @property
    def current_market_price(self):
        """Get current market price from data insights (integrated after data_insights app)"""
        try:
            from data_insights.models import MarketPrice
            from django.utils import timezone
            from datetime import timedelta
            
            # Get latest market price within last 30 days
            recent_price = MarketPrice.objects.filter(
                product=self,
                price_date__gte=timezone.now().date() - timedelta(days=30)
            ).order_by('-price_date').first()
            
            return {
                'average': recent_price.average_price if recent_price else None,
                'min': recent_price.min_price if recent_price else None,
                'max': recent_price.max_price if recent_price else None,
                'date': recent_price.price_date if recent_price else None
            }
        except ImportError:
            return None

class ProductListing(models.Model):
    """Model representing specific product listings by farmers"""
    QUALITY_GRADE_CHOICES = (
        ('premium', 'Premium'),
        ('standard', 'Standard'),
        ('economy', 'Economy'),
    )
    
    LISTING_STATUS_CHOICES = (
        ('available', 'Available'),
        ('pre_order', 'Pre-order'),
        ('sold_out', 'Sold Out'),
        ('inactive', 'Inactive'),
    )
    
    listing_id = models.AutoField(primary_key=True)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_listings')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='product_listings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    harvest_date = models.DateField(null=True, blank=True)
    expected_harvest_date = models.DateField(null=True, blank=True)
    quality_grade = models.CharField(max_length=10, choices=QUALITY_GRADE_CHOICES, default='standard')
    is_organic_certified = models.BooleanField(default=False)
    listing_status = models.CharField(max_length=15, choices=LISTING_STATUS_CHOICES, default='available')
    photos = models.JSONField(default=list, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Product_Listings'
        indexes = [
            models.Index(fields=['farmer']),
            models.Index(fields=['product']),
            models.Index(fields=['listing_status']),
            models.Index(fields=['harvest_date']),
        ]
    
    def __str__(self):
        return f"{self.product.product_name} by {self.farmer.get_full_name()} - {self.get_listing_status_display()}"
    
    def save(self, *args, **kwargs):
        # If this is a new listing, copy the is_organic_certified value from the farm
        if not self.pk and self.farm and not self.is_organic_certified:
            self.is_organic_certified = self.farm.is_certified_organic
        super().save(*args, **kwargs)
    
    @property
    def farmer_rating(self):
        """Get farmer's average rating from reviews (integrated after feedback app)"""
        try:
            from feedback.models import Review
            reviews = Review.objects.filter(
                target_type='farmer',
                target_id=str(self.farmer.user_id),
                is_visible=True
            )
            return reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        except ImportError:
            return 0
    
    @property
    def price_comparison(self):
        """Compare listing price with market price (integrated after data_insights app)"""
        market_price = self.product.current_market_price
        if not market_price or not market_price['average']:
            return None
        
        difference = float(self.current_price) - float(market_price['average'])
        percentage = (difference / float(market_price['average'])) * 100
        
        return {
            'market_average': market_price['average'],
            'listing_price': self.current_price,
            'difference': difference,
            'percentage': percentage,
            'status': 'above_market' if difference > 0 else 'below_market' if difference < 0 else 'at_market'
        }
    
    def check_weather_alerts(self):
        """Check for relevant weather alerts for this listing (integrated after data_insights app)"""
        try:
            from data_insights.models import WeatherAlert
            from django.utils import timezone
            
            return WeatherAlert.objects.filter(
                location=self.farm.location,
                is_active=True,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            )
        except ImportError:
            return []