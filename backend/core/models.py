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
                'setting_key': 'vat_rate',
                'setting_value': '0.16',
                'setting_type': 'number',
                'description': 'VAT rate (16%)'
            },
            {
                'setting_key': 'transaction_fee_rate',
                'setting_value': '0.02',
                'setting_type': 'number',
                'description': 'Transaction fee rate (2%)'
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
