from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from orders.models import OrderItem

class Review(models.Model):
    """Model for product, farmer, and rider reviews"""
    TARGET_TYPES = (
        ('product', 'Product'),
        ('farmer', 'Farmer'),
        ('rider', 'Rider'),
    )
    
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    target_type = models.CharField(max_length=10, choices=TARGET_TYPES)
    target_id = models.UUIDField()  # ID of product, farmer, or rider
    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    comment = models.TextField(null=True, blank=True)
    review_photos = models.JSONField(default=list, blank=True)
    is_verified_purchase = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    review_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-review_date']
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['order_item']),
        ]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.reviewer.phone_number}'s {self.rating} star review of {self.target_type}"
