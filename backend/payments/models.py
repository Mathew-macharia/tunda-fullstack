from django.db import models
from django.conf import settings
from decimal import Decimal
from orders.models import Order

class PaymentMethod(models.Model):
    """
    Payment method model to store different payment options for users
    """
    PAYMENT_TYPE_CHOICES = [
        ('Mpesa', 'Mpesa'),
        ('CashOnDelivery', 'Cash On Delivery'),
        ('BankTransfer', 'Bank Transfer'),
    ]
    
    payment_method_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    mpesa_phone = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Payment_Methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['payment_type']),
        ]
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.user.phone_number}"
    
    def save(self, *args, **kwargs):
        # If this payment method is set as default, unset all other defaults for this user
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        # If this is the first payment method for the user, set it as default
        if not self.pk and not PaymentMethod.objects.filter(user=self.user).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)

class PaymentTransaction(models.Model):
    """
    Payment transaction model to log all payment attempts
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Payment_Transactions'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} - {self.payment_status}"
    
    def update_order_status(self):
        """
        Update the associated order's payment and order status based on this transaction
        """
        if self.payment_status == 'completed':
            # Update order payment status to paid
            self.order.payment_status = 'paid'
            
            # If order is in pending_payment status, move to confirmed
            if self.order.order_status == 'pending_payment':
                self.order.order_status = 'confirmed'
                
            self.order.save()
        elif self.payment_status == 'failed':
            # If payment fails, keep order in pending_payment state
            self.order.payment_status = 'failed'
            self.order.save()
        elif self.payment_status == 'cancelled':
            # If payment is cancelled, update order payment status
            self.order.payment_status = 'cancelled'
            self.order.save()
