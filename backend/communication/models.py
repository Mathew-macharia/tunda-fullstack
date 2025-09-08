from django.db import models
import uuid
from users.models import User
from django.utils import timezone
from django.apps import apps # Import apps to resolve circular dependency

# Defer Order import to avoid circular dependency
# Order = apps.get_model('orders', 'Order') # This line is not needed here, but for reference

class Notification(models.Model):
    """Model for system notifications"""
    NOTIFICATION_TYPES = (
        ('order_update', 'Order Update'),
        ('payment_received', 'Payment Received'),
        ('weather_alert', 'Weather Alert'),
        ('price_update', 'Price Update'),
        ('system_message', 'System Message'),
        ('marketing', 'Marketing'),
    )
    
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    related_id = models.CharField(max_length=255, null=True, blank=True)  # ID of related entity (changed to CharField)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.title} - {self.user.phone_number}"


class Message(models.Model):
    """Model for user-to-user messaging"""
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('audio', 'Audio'),
        ('image', 'Image'),
    )
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # Use a string reference for Order to avoid circular import
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    message_text = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    media_url = models.URLField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['sender']),
            models.Index(fields=['order']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"Message from {self.sender.phone_number} to {self.recipient.phone_number}"


class SupportTicket(models.Model):
    """Model for customer support tickets"""
    CATEGORY_CHOICES = (
        ('order_issue', 'Order Issue'),
        ('payment_problem', 'Payment Problem'),
        ('delivery_issue', 'Delivery Issue'),
        ('product_quality', 'Product Quality'),
        ('technical_support', 'Technical Support'),
        ('other', 'Other'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    # Use a string reference for Order to avoid circular import
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    ticket_number = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    resolution_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['ticket_number']),
        ]
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
    
    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        """Generate a unique ticket number on creation"""
        if not self.ticket_number:
            # Format: TKT-YYYYMMDD-XXXX where XXXX is a random number
            today = timezone.now().strftime('%Y%m%d')
            random_id = uuid.uuid4().hex[:4].upper()
            self.ticket_number = f"TKT-{today}-{random_id}"
        
        # Set resolved_at timestamp if status changes to resolved or closed
        if self.status in ['resolved', 'closed'] and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)


class FAQ(models.Model):
    """Model for Frequently Asked Questions"""
    faq_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    target_role = models.CharField(max_length=10, choices=[
        ('customer', 'Customer'),
        ('farmer', 'Farmer'), 
        ('rider', 'Rider'),
        ('all', 'All Users')
    ], default='all')
    is_active = models.BooleanField(default=True)
    order_index = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order_index', 'created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return f"{self.question} ({self.target_role})"
