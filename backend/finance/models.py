from django.db import models
from django.conf import settings
import uuid
from orders.models import Order

class Payout(models.Model):
    """Model for tracking payments from the platform to farmers/riders"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )
    
    payout_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    payout_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-payout_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payout_date']),
            models.Index(fields=['order']),
        ]
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
    
    def __str__(self):
        return f"Payout {self.payout_id} - {self.user.phone_number} - {self.amount}"
