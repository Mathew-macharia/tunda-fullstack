from django.db import models
from django.conf import settings
from locations.models import SubCounty
from django.db.models import Sum, Avg
from django.utils import timezone


class Farm(models.Model):
    WEATHER_ZONE_CHOICES = (
        ('highland', 'Highland'),
        ('midland', 'Midland'),
        ('lowland', 'Lowland'),
    )
    
    SOIL_TYPE_CHOICES = (
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loamy', 'Loamy'),
        ('silt', 'Silt'),
        ('peaty', 'Peaty'),
        ('chalky', 'Chalky'),
    )
    
    WATER_SOURCE_CHOICES = (
        ('borehole', 'Borehole'),
        ('river', 'River'),
        ('rain', 'Rain Water'),
        ('well', 'Well'),
        ('municipal', 'Municipal Supply'),
        ('dam', 'Dam'),
    )
    
    farm_id = models.AutoField(primary_key=True)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    farm_name = models.CharField(max_length=255)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='farms')
    total_acreage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cultivated_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Area currently under cultivation")
    farm_description = models.TextField(blank=True, null=True)
    farm_photos = models.JSONField(default=list, blank=True, null=True)
    is_certified_organic = models.BooleanField(default=False)
    soil_type = models.CharField(max_length=10, choices=SOIL_TYPE_CHOICES, blank=True, null=True)
    water_source = models.CharField(max_length=10, choices=WATER_SOURCE_CHOICES, blank=True, null=True)
    weather_zone = models.CharField(max_length=10, choices=WEATHER_ZONE_CHOICES, default='highland')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Farms'
        indexes = [
            models.Index(fields=['farmer']),
            models.Index(fields=['sub_county']),
        ]
    
    def __str__(self):
        return f"{self.farm_name} - {self.farmer.get_full_name()}"
    
    @property
    def location_name(self):
        """Get location name from subcounty and county"""
        return f"{self.sub_county.sub_county_name}, {self.sub_county.county.county_name}"
    
    @property
    def active_weather_alerts(self):
        """Get active weather alerts for this farm (integrated after data_insights app)"""
        try:
            from data_insights.models import WeatherAlert
            from django.utils import timezone
            
            return WeatherAlert.objects.filter(
                location=self.sub_county,
                is_active=True,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            )
        except ImportError:
            return []
    
    @property
    def total_earnings(self):
        """Calculate total earnings from all orders (integrated after orders app)"""
        try:
            from orders.models import OrderItem
            
            earnings = OrderItem.objects.filter(
                farmer=self.farmer,
                listing__farm=self,
                order__payment_status='paid'
            ).aggregate(total=Sum('total_price'))['total']
            
            return earnings or 0
        except ImportError:
            return 0
    
    @property
    def pending_payouts(self):
        """Get total pending payouts for this farm (integrated after finance app)"""
        try:
            from finance.models import Payout
            
            pending = Payout.objects.filter(
                user=self.farmer,
                status='pending'
            ).aggregate(total=Sum('amount'))['total']
            
            return pending or 0
        except ImportError:
            return 0
    
    @property
    def farmer_rating(self):
        """Get farmer's average rating (integrated after feedback app)"""
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
    def active_listings_count(self):
        """Get count of active product listings from this farm"""
        return self.product_listings.filter(
            listing_status__in=['available', 'pre_order']
        ).count()
    
    @property
    def products_variety(self):
        """Get count of different products listed from this farm"""
        return self.product_listings.values('product').distinct().count()
    
    def get_recent_market_prices(self, days=30):
        """Get recent market prices for products from this farm (integrated after data_insights app)"""
        try:
            from data_insights.models import MarketPrice
            from datetime import timedelta
            
            farm_products = self.product_listings.values_list('product', flat=True).distinct()
            
            return MarketPrice.objects.filter(
                product__in=farm_products,
                location=self.sub_county,
                price_date__gte=timezone.now().date() - timedelta(days=days)
            ).order_by('-price_date')
        except ImportError:
            return []
