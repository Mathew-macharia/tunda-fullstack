from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('farmer', 'Farmer'),
        ('rider', 'Rider'),
        ('admin', 'Admin'),
    )
    
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('sw', 'Swahili'),
        ('kikuyu', 'Kikuyu'),
    )
    
    # Field mapping to your database schema
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    # password is handled by AbstractBaseUser
    user_role = models.CharField(max_length=10, choices=USER_ROLES)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    profile_photo_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='sw')
    
    # Notification and Communication Preferences (Added after communication app)
    sms_notifications = models.BooleanField(default=True, help_text="Receive SMS notifications")
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications")
    marketing_notifications = models.BooleanField(default=False, help_text="Receive marketing messages")
    order_updates = models.BooleanField(default=True, help_text="Receive order status updates")
    weather_alerts = models.BooleanField(default=True, help_text="Receive weather alerts (farmers only)")
    price_alerts = models.BooleanField(default=True, help_text="Receive price update alerts")
    
    # Additional user settings
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Phone number verification status")
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_expires = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields required by Django
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_role']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def unread_notifications_count(self):
        """Get count of unread notifications for this user"""
        if hasattr(self, 'notifications'):
            return self.notifications.filter(is_read=False).count()
        return 0
    
    @property
    def unread_messages_count(self):
        """Get count of unread messages for this user"""
        if hasattr(self, 'received_messages'):
            return self.received_messages.filter(is_read=False).count()
        return 0
    
    def should_receive_notification(self, notification_type):
        """Check if user should receive a specific type of notification"""
        preferences = {
            'order_update': self.order_updates,
            'weather_alert': self.weather_alerts and self.user_role == 'farmer',
            'price_update': self.price_alerts,
            'marketing': self.marketing_notifications,
            'system_message': True,  # Always send system messages
            'payment_received': True,  # Always send payment confirmations
        }
        return preferences.get(notification_type, True)