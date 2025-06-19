from django.db import models
import uuid
from products.models import Product
from locations.models import Location

class MarketPrice(models.Model):
    """Model for tracking historical product prices"""
    DATA_SOURCE_CHOICES = (
        ('platform', 'Platform'),
        ('market_survey', 'Market Survey'),
        ('government', 'Government'),
    )
    
    price_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='market_prices')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='market_prices')
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_date = models.DateField()
    data_source = models.CharField(max_length=15, choices=DATA_SOURCE_CHOICES, default='platform')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-price_date']
        indexes = [
            models.Index(fields=['product', 'price_date']),
            models.Index(fields=['location']),
            models.Index(fields=['data_source']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'location', 'price_date'],
                name='unique_price_record'
            )
        ]
        verbose_name = 'Market Price'
        verbose_name_plural = 'Market Prices'
    
    def __str__(self):
        return f"{self.product.product_name} price in {self.location.location_name} on {self.price_date}"


class WeatherAlert(models.Model):
    """Model for weather alerts and forecasts"""
    ALERT_TYPE_CHOICES = (
        ('rain', 'Rain'),
        ('drought', 'Drought'),
        ('frost', 'Frost'),
        ('hail', 'Hail'),
        ('wind', 'Wind'),
        ('flood', 'Flood'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    alert_message = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location', 'start_date']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Weather Alert'
        verbose_name_plural = 'Weather Alerts'
    
    def __str__(self):
        return f"{self.get_alert_type_display()} alert for {self.location.location_name} - {self.get_severity_display()} severity"
