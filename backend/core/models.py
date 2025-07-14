from django.db import models
import json
from decimal import Decimal

class SystemSettingsManager(models.Manager):
    """
    Custom manager for SystemSettings to provide helper methods for retrieving settings by key and type
    """
    def get_setting(self, key, default=None):
        """
        Get a setting by key, return default if not found
        """
        try:
            setting = self.get(setting_key=key)
            return self._convert_value(setting.setting_value, setting.setting_type)
        except SystemSettings.DoesNotExist:
            return default
    
    def _convert_value(self, value, value_type):
        """
        Convert value to its appropriate type based on setting_type
        """
        if value_type == 'string':
            return value
        elif value_type == 'number':
            try:
                return Decimal(value)
            except:
                return 0
        elif value_type == 'boolean':
            return value.lower() == 'true'
        elif value_type == 'json':
            try:
                return json.loads(value)
            except:
                return {}
        return value
    
    def initialize_default_settings(self):
        """Create default system settings if they don't exist"""
        default_settings = [
            {
                'setting_key': 'base_delivery_fee',
                'setting_value': '50.00',
                'setting_type': 'number',
                'description': 'Base delivery fee in KES'
            },
            {
                'setting_key': 'free_delivery_threshold',
                'setting_value': '1000.00',
                'setting_type': 'number',
                'description': 'Minimum order amount for free delivery in KES'
            },
            {
                'setting_key': 'weight_threshold_light',
                'setting_value': '10.00',
                'setting_type': 'number',
                'description': 'Weight threshold for light surcharge in kg'
            },
            {
                'setting_key': 'weight_surcharge_light',
                'setting_value': '15.00',
                'setting_type': 'number',
                'description': 'Additional delivery fee for orders over light weight threshold in KES'
            },
            {
                'setting_key': 'weight_threshold_heavy',
                'setting_value': '20.00',
                'setting_type': 'number',
                'description': 'Weight threshold for heavy surcharge in kg'
            },
            {
                'setting_key': 'weight_surcharge_heavy',
                'setting_value': '30.00',
                'setting_type': 'number',
                'description': 'Additional delivery fee for orders over heavy weight threshold in KES'
            },
            {
                'setting_key': 'vat_rate',
                'setting_value': '0.16',
                'setting_type': 'number',
                'description': 'VAT rate (16%)'
            },
            {
                'setting_key': 'transaction_fee_rate',
                'setting_value': '0.015',
                'setting_type': 'number',
                'description': 'Transaction fee rate (1.5%)'
            },
            {
                'setting_key': 'platform_fee_rate',
                'setting_value': '0.10',
                'setting_type': 'number',
                'description': 'Platform fee rate (10%)'
            },
            {
                'setting_key': 'max_delivery_radius_km',
                'setting_value': '50',
                'setting_type': 'number',
                'description': 'Maximum delivery radius in kilometers'
            },
            {
                'setting_key': 'order_cancellation_window_hours',
                'setting_value': '24',
                'setting_type': 'number',
                'description': 'Hours within which customers can cancel orders'
            },
            {
                'setting_key': 'sms_notifications_enabled',
                'setting_value': 'true',
                'setting_type': 'boolean',
                'description': 'Enable SMS notifications system-wide'
            },
            {
                'setting_key': 'email_notifications_enabled',
                'setting_value': 'true',
                'setting_type': 'boolean',
                'description': 'Enable email notifications system-wide'
            },
            {
                'setting_key': 'supported_payment_methods',
                'setting_value': '["Mpesa", "CashOnDelivery", "BankTransfer"]',
                'setting_type': 'json',
                'description': 'List of supported payment methods'
            },
            {
                'setting_key': 'delivery_fee_per_km',
                'setting_value': '5.00',
                'setting_type': 'number',
                'description': 'Delivery fee per kilometer in KES'
            },
            {
                'setting_key': 'max_delivery_distance_km',
                'setting_value': '50',
                'setting_type': 'number',
                'description': 'Maximum delivery distance in kilometers'
            },
            {
                'setting_key': 'multi_farm_consolidation_fee',
                'setting_value': '25.00',
                'setting_type': 'number',
                'description': 'Additional fee per extra farm in multi-farm orders'
            },
            {
                'setting_key': 'wht_rate',
                'setting_value': '0.03',
                'setting_type': 'number',
                'description': 'Withholding Tax rate (3%) for riders'
            },
            {
                'setting_key': 'wht_threshold',
                'setting_value': '24000.00',
                'setting_type': 'number',
                'description': 'Withholding Tax threshold in KES for riders'
            },
            # M-Pesa API Settings
            {
                'setting_key': 'mpesa_consumer_key',
                'setting_value': '',
                'setting_type': 'string',
                'description': 'M-Pesa API Consumer Key from Daraja Portal'
            },
            {
                'setting_key': 'mpesa_consumer_secret',
                'setting_value': '',
                'setting_type': 'string',
                'description': 'M-Pesa API Consumer Secret from Daraja Portal'
            },
            {
                'setting_key': 'mpesa_business_shortcode',
                'setting_value': '',
                'setting_type': 'string',
                'description': 'M-Pesa Business Shortcode (Till/PayBill Number)'
            },
            {
                'setting_key': 'mpesa_passkey',
                'setting_value': '',
                'setting_type': 'string',
                'description': 'M-Pesa STK Push Passkey'
            },
            {
                'setting_key': 'mpesa_environment',
                'setting_value': 'sandbox',
                'setting_type': 'string',
                'description': 'M-Pesa Environment (sandbox/production)'
            },
            {
                'setting_key': 'mpesa_callback_url',
                'setting_value': 'https://yourdomain.com/api/payments/transactions/mpesa_callback/',
                'setting_type': 'string',
                'description': 'M-Pesa Callback URL for payment notifications'
            },
            {
                'setting_key': 'min_withdrawal_amount',
                'setting_value': '200.00',
                'setting_type': 'number',
                'description': 'Minimum amount allowed for a withdrawal in KES'
            },
            {
                'setting_key': 'clearance_threshold_amount',
                'setting_value': '20000.00',
                'setting_type': 'number',
                'description': 'Withdrawal amount threshold for 24-48 hour clearance in KES'
            }
        ]
        
        for setting in default_settings:
            self.get_or_create(
                setting_key=setting['setting_key'],
                defaults={
                    'setting_value': setting['setting_value'],
                    'setting_type': setting['setting_type'],
                    'description': setting['description']
                }
            )

class SystemSettings(models.Model):
    """
    System settings for platform configuration
    """
    SETTING_TYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    
    setting_id = models.AutoField(primary_key=True)
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    setting_type = models.CharField(max_length=10, choices=SETTING_TYPE_CHOICES, default='string')
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = SystemSettingsManager()
    
    class Meta:
        db_table = 'System_Settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['setting_key']
    
    def __str__(self):
        return f"{self.setting_key}: {self.setting_value}"
    
    def get_typed_value(self):
        """
        Get the value converted to its appropriate type
        """
        return SystemSettings.objects._convert_value(self.setting_value, self.setting_type)

class PopularPlace(models.Model):
    """
    Popular places and landmarks for address validation and autocomplete
    """
    PLACE_TYPES = [
        ('shopping', 'Shopping Center/Mall'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('attraction', 'Tourist Attraction'),
        ('park', 'Park/Recreation'),
        ('business', 'Business District'),
        ('area', 'Residential/Commercial Area'),
        ('education', 'Educational Institution'),
        ('hospital', 'Hospital/Medical'),
        ('transport', 'Transport Hub'),
        ('government', 'Government Office'),
        ('religious', 'Religious Site'),
        ('other', 'Other'),
    ]
    
    place_id = models.AutoField(primary_key=True)
    place_name = models.CharField(max_length=200, db_index=True)
    place_type = models.CharField(max_length=20, choices=PLACE_TYPES, default='other')
    sub_county = models.ForeignKey('locations.SubCounty', on_delete=models.CASCADE, related_name='popular_places')
    alternative_names = models.JSONField(default=list, blank=True, help_text="Alternative names/spellings for this place")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Whether this place has been verified")
    popularity_score = models.IntegerField(default=0, help_text="Higher score = more popular")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'PopularPlaces'
        indexes = [
            models.Index(fields=['place_name']),
            models.Index(fields=['place_type']),
            models.Index(fields=['sub_county']),
            models.Index(fields=['popularity_score']),
        ]
        unique_together = ['place_name', 'sub_county']
    
    def __str__(self):
        return f"{self.place_name} ({self.sub_county.sub_county_name})"

class AddressValidationCache(models.Model):
    """
    Cache for address validation results to improve performance
    """
    cache_id = models.AutoField(primary_key=True)
    address_hash = models.CharField(max_length=64, unique=True, db_index=True)
    detailed_address = models.TextField()
    sub_county = models.ForeignKey('locations.SubCounty', on_delete=models.CASCADE, null=True, blank=True)
    validation_result = models.JSONField()
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    
    class Meta:
        db_table = 'AddressValidationCache'
        indexes = [
            models.Index(fields=['address_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache for {self.detailed_address[:50]}..."
