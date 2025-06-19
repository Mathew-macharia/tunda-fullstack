from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from products.models import ProductListing
from locations.models import Location
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

# Import will be resolved after migration
# Using string reference to avoid circular import issues


class Order(models.Model):
    """Model representing a customer's order"""
    ORDER_STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    DELIVERY_TIME_SLOT_CHOICES = [
        ('morning', 'Morning (8am - 12pm)'),
        ('afternoon', 'Afternoon (12pm - 4pm)'),
        ('evening', 'Evening (4pm - 8pm)'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,  # Protect to preserve order history
        related_name='delivery_orders'
    )
    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.PROTECT,  # Protect to preserve order history
        related_name='orders',
        null=True,
        blank=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending_payment'
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    estimated_delivery_date = models.DateField(null=True, blank=True)
    delivery_time_slot = models.CharField(
        max_length=10,
        choices=DELIVERY_TIME_SLOT_CHOICES,
        null=True, 
        blank=True
    )
    special_instructions = models.TextField(blank=True, null=True)
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='delivery_orders',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['order_status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['estimated_delivery_date']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        # Generate a unique order number if not already set
        if not self.order_number:
            prefix = 'TUN'
            timestamp = str(int(self.created_at.timestamp())) if self.created_at else ''
            random_str = get_random_string(4, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.order_number = f"{prefix}{timestamp[-6:]}{random_str}"
            
            # Ensure the order number is unique
            while Order.objects.filter(order_number=self.order_number).exists():
                random_str = get_random_string(4, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                self.order_number = f"{prefix}{timestamp[-6:]}{random_str}"
        
        super().save(*args, **kwargs)

    def get_farmers(self):
        """Get all farmers involved in this order"""
        return set(item.farmer for item in self.items.all())
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.order_status in ['pending_payment', 'confirmed']
    
    def calculate_delivery_fee(self):
        """Calculate delivery fee based on location and order contents"""
        try:
            from core.models import SystemSettings
            from decimal import Decimal
            
            base_fee = SystemSettings.objects.get_setting('base_delivery_fee', Decimal('50.00'))
            free_delivery_threshold = SystemSettings.objects.get_setting('free_delivery_threshold', Decimal('1000.00'))
            
            if self.total_amount >= free_delivery_threshold:
                return Decimal('0.00')
            
            return base_fee
        except:
            return self.delivery_fee or 0


class OrderItem(models.Model):
    """Model representing an item in a customer's order"""
    ITEM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('harvested', 'Harvested'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
    ]
    
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    listing = models.ForeignKey(
        ProductListing,
        on_delete=models.PROTECT,  # Protect to preserve order history
        related_name='order_items'
    )
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Protect to preserve order history
        related_name='sold_items'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    item_status = models.CharField(
        max_length=10,
        choices=ITEM_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['farmer']),
        ]
    
    def __str__(self):
        return f"{self.quantity} of {self.listing.product.product_name} in Order #{self.order.order_number}"


# Signal handlers for automatic notifications and business logic

@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """Send notifications when order is created or status changes"""
    if not created:
        return
        
    print(f"DEBUG: Order {instance.order_id} created, sending notifications...")
    
    try:
        from communication.models import Notification
        print(f"DEBUG: Successfully imported Notification model")
        
        # Send order confirmation to customer
        if instance.customer.should_receive_notification('order_update'):
            print(f"DEBUG: Creating customer notification for order {instance.order_id}")
            print(f"DEBUG: Customer: {instance.customer}")
            print(f"DEBUG: Customer SMS: {instance.customer.sms_notifications}")
            try:
                notification = Notification.objects.create(
                    user=instance.customer,
                    notification_type='order_update',
                    title=f'Order Confirmed #{instance.order_number}',
                    message=f'Your order for KES {instance.total_amount} has been confirmed and is being processed.',
                    send_sms=instance.customer.sms_notifications
                )
                print(f"DEBUG: Customer notification created successfully: {notification.notification_id}")
            except Exception as e:
                print(f"DEBUG: Error creating customer notification: {e}")
                import traceback
                traceback.print_exc()
        
        # Notify farmers about new orders
        farmers = instance.get_farmers()
        print(f"DEBUG: Found {len(farmers)} farmers for this order")
        print(f"DEBUG: Order items: {list(instance.items.all())}")
        
        for farmer in farmers:
            if farmer.should_receive_notification('order_update'):
                farmer_items = instance.items.filter(farmer=farmer)
                total_farmer_amount = sum(item.total_price for item in farmer_items)
                
                print(f"DEBUG: Creating farmer notification for {farmer}")
                try:
                    notification = Notification.objects.create(
                        user=farmer,
                        notification_type='order_update',
                        title=f'New Order Received #{instance.order_number}',
                        message=f'You have received a new order worth KES {total_farmer_amount}. Please prepare the items for delivery.',
                        send_sms=farmer.sms_notifications
                    )
                    print(f"DEBUG: Farmer notification created successfully: {notification.notification_id}")
                except Exception as e:
                    print(f"DEBUG: Error creating farmer notification: {e}")
                    import traceback
                    traceback.print_exc()
        
    except ImportError as e:
        print(f"DEBUG: Communication app not available: {e}")
    except Exception as e:
        print(f"DEBUG: Unexpected error in send_order_notifications: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise the exception - let the order creation succeed

@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """Track order status changes and send appropriate notifications"""
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Status changed
            if old_instance.order_status != instance.order_status:
                # Handle specific status changes
                if instance.order_status == 'confirmed' and old_instance.order_status == 'pending_payment':
                    # Order confirmed, create delivery record
                    try:
                        from delivery.models import Delivery
                        
                        # Create delivery record if it doesn't exist
                        if not hasattr(instance, 'delivery'):
                            Delivery.objects.create(
                                order=instance,
                                delivery_status='pending_pickup'
                            )
                    except ImportError:
                        pass
                
                # Send status update notifications
                try:
                    from communication.models import Notification
                    
                    status_messages = {
                        'confirmed': 'Your order has been confirmed and is being prepared.',
                        'processing': 'Your order is being processed by our farmers.',
                        'out_for_delivery': 'Your order is out for delivery.',
                        'delivered': 'Your order has been delivered successfully.',
                        'cancelled': 'Your order has been cancelled.',
                    }
                    
                    if instance.order_status in status_messages:
                        if instance.customer.should_receive_notification('order_update'):
                            Notification.objects.create(
                                user=instance.customer,
                                notification_type='order_update',
                                title=f'Order Update #{instance.order_number}',
                                message=status_messages[instance.order_status],
                                send_sms=instance.customer.sms_notifications
                            )
                
                except ImportError:
                    pass
                    
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=OrderItem)
def send_order_item_notifications(sender, instance, created, **kwargs):
    """Send notifications when order item status changes"""
    if not created:  # Only for updates
        try:
            from communication.models import Notification
            
            status_messages = {
                'harvested': f'Your {instance.listing.product.product_name} has been harvested and is ready for packing.',
                'packed': f'Your {instance.listing.product.product_name} has been packed and is ready for delivery.',
                'delivered': f'Your {instance.listing.product.product_name} has been delivered.',
            }
            
            if instance.item_status in status_messages:
                if instance.order.customer.should_receive_notification('order_update'):
                    Notification.objects.create(
                        user=instance.order.customer,
                        notification_type='order_update',
                        title=f'Item Update - Order #{instance.order.order_number}',
                        message=status_messages[instance.item_status],
                        send_sms=instance.order.customer.sms_notifications
                    )
        
        except ImportError:
            pass
