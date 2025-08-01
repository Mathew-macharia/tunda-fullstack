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
    
    def calculate_delivery_fee(self, delivery_location=None):
        """
        CENTRALIZED delivery fee calculation - Single Source of Truth
        Calculate delivery fee based on order contents, weight, location, and business rules
        """
        try:
            from core.models import SystemSettings
            from decimal import Decimal
            
            # Get system settings
            base_fee = SystemSettings.objects.get_setting('base_delivery_fee', Decimal('50.00'))
            free_delivery_threshold = SystemSettings.objects.get_setting('free_delivery_threshold', Decimal('1000.00'))
            weight_threshold_light = SystemSettings.objects.get_setting('weight_threshold_light', Decimal('10.00'))
            weight_surcharge_light = SystemSettings.objects.get_setting('weight_surcharge_light', Decimal('15.00'))
            weight_threshold_heavy = SystemSettings.objects.get_setting('weight_threshold_heavy', Decimal('20.00'))
            weight_surcharge_heavy = SystemSettings.objects.get_setting('weight_surcharge_heavy', Decimal('30.00'))
            
            # Calculate subtotal (items only, excluding delivery fee)
            items_total = sum(item.total_price for item in self.items.all())
            
            # Free delivery threshold check
            if items_total >= free_delivery_threshold:
                return Decimal('0.00')
            
            # Start with base fee
            total_fee = base_fee
            
            # Calculate weight-based surcharge
            total_weight = Decimal('0.00')
            for item in self.items.all():
                if item.listing.product.unit_of_measure == 'kg':
                    total_weight += item.quantity
            
            # Apply weight surcharges
            if total_weight > weight_threshold_heavy:
                total_fee += weight_surcharge_heavy
            elif total_weight > weight_threshold_light:
                total_fee += weight_surcharge_light
            
            # Distance-based fee calculation
            distance_fee = Decimal('0.00')
            if delivery_location:
                try:
                    from core.services.address_service import AddressService
                    
                    address_service = AddressService()
                    
                    # Get customer coordinates
                    customer_coords = address_service.get_customer_coordinates(delivery_location)
                    
                    # Get all farms involved in this order
                    farms = set(item.listing.farm for item in self.items.all())
                    
                    if len(farms) == 1:
                        # Single farm delivery
                        farm = list(farms)[0]
                        farm_coords = address_service.get_farm_coordinates(farm)
                        distance_km = address_service.calculate_distance(farm_coords, customer_coords)
                        
                        # Apply distance-based fee
                        fee_per_km = SystemSettings.objects.get_setting('delivery_fee_per_km', Decimal('5.00'))
                        distance_fee = Decimal(str(distance_km)) * fee_per_km
                        
                    else:
                        # Multi-farm delivery - use farthest farm + consolidation fee
                        max_distance = Decimal('0.00')
                        
                        for farm in farms:
                            farm_coords = address_service.get_farm_coordinates(farm)
                            distance_km = address_service.calculate_distance(farm_coords, customer_coords)
                            max_distance = max(max_distance, Decimal(str(distance_km)))
                        
                        # Base distance fee (farthest farm)
                        fee_per_km = SystemSettings.objects.get_setting('delivery_fee_per_km', Decimal('5.00'))
                        distance_fee = max_distance * fee_per_km
                        
                        # Add consolidation fee for additional farms
                        consolidation_fee = SystemSettings.objects.get_setting('multi_farm_consolidation_fee', Decimal('25.00'))
                        distance_fee += consolidation_fee * (len(farms) - 1)
                        
                except Exception as e:
                    print(f"Distance calculation error: {e}")
                    # Fallback to no distance fee
                    distance_fee = Decimal('0.00')
            
            total_fee += distance_fee
            
            return total_fee
            
        except Exception as e:
            # Fallback to existing delivery fee or base fee
            return self.delivery_fee if self.delivery_fee else Decimal('50.00')
    
    @staticmethod
    def calculate_delivery_fee_for_cart(cart_items, delivery_location=None):
        """
        Calculate delivery fee for cart items before order creation
        Static method to estimate delivery fee during cart/checkout process
        """
        try:
            from core.models import SystemSettings
            from decimal import Decimal
            
            # Get system settings
            base_fee = SystemSettings.objects.get_setting('base_delivery_fee', Decimal('50.00'))
            free_delivery_threshold = SystemSettings.objects.get_setting('free_delivery_threshold', Decimal('1000.00'))
            weight_threshold_light = SystemSettings.objects.get_setting('weight_threshold_light', Decimal('10.00'))
            weight_surcharge_light = SystemSettings.objects.get_setting('weight_surcharge_light', Decimal('15.00')) 
            weight_threshold_heavy = SystemSettings.objects.get_setting('weight_threshold_heavy', Decimal('20.00')) 
            weight_surcharge_heavy = SystemSettings.objects.get_setting('weight_surcharge_heavy', Decimal('30.00'))
            
            # Calculate subtotal from cart items
            items_total = sum(item.quantity * item.price_at_addition for item in cart_items)
            
            # Free delivery threshold check
            if items_total >= free_delivery_threshold:
                return Decimal('0.00')
            
            # Start with base fee
            total_fee = base_fee
            
            # Calculate weight-based surcharge
            total_weight = Decimal('0.00')
            for item in cart_items:
                if item.listing.product.unit_of_measure == 'kg':
                    total_weight += item.quantity
            
            # Apply weight surcharges
            if total_weight > weight_threshold_heavy:
                total_fee += weight_surcharge_heavy
            elif total_weight > weight_threshold_light:
                total_fee += weight_surcharge_light
            
            # Distance-based fee calculation
            distance_fee = Decimal('0.00')
            if delivery_location:
                try:
                    from core.services.address_service import AddressService
                    
                    address_service = AddressService()
                    
                    # Get customer coordinates
                    customer_coords = address_service.get_customer_coordinates(delivery_location)
                    
                    # Get all farms involved in cart
                    farms = set(item.listing.farm for item in cart_items)
                    
                    if len(farms) == 1:
                        # Single farm delivery
                        farm = list(farms)[0]
                        farm_coords = address_service.get_farm_coordinates(farm)
                        distance_km = address_service.calculate_distance(farm_coords, customer_coords)
                        
                        # Apply distance-based fee
                        fee_per_km = SystemSettings.objects.get_setting('delivery_fee_per_km', Decimal('5.00'))
                        distance_fee = Decimal(str(distance_km)) * fee_per_km
                        
                    else:
                        # Multi-farm delivery - use farthest farm + consolidation fee
                        max_distance = Decimal('0.00')
                        
                        for farm in farms:
                            farm_coords = address_service.get_farm_coordinates(farm)
                            distance_km = address_service.calculate_distance(farm_coords, customer_coords)
                            max_distance = max(max_distance, Decimal(str(distance_km)))
                        
                        # Base distance fee (farthest farm)
                        fee_per_km = SystemSettings.objects.get_setting('delivery_fee_per_km', Decimal('5.00'))
                        distance_fee = max_distance * fee_per_km
                        
                        # Add consolidation fee for additional farms
                        consolidation_fee = SystemSettings.objects.get_setting('multi_farm_consolidation_fee', Decimal('25.00'))
                        distance_fee += consolidation_fee * (len(farms) - 1)
                        
                except Exception as e:
                    print(f"Distance calculation error: {e}")
                    # Fallback to no distance fee
                    distance_fee = Decimal('0.00')
            
            total_fee += distance_fee
            
            return total_fee
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error during delivery fee calculation in Order.calculate_delivery_fee_for_cart. Falling back to 50.00 KES.")
            # Fallback to base fee
            return Decimal('50.00')


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

@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """
    Tracks order status changes and stores the original status for post_save.
    Also creates a Delivery record when an order is confirmed.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._original_order_status = old_instance.order_status
            
            # The Delivery record is now created by PaymentSession.create_order_from_session
            # or by an admin. This signal no longer creates it.
            pass 
        except sender.DoesNotExist:
            instance._original_order_status = None # New order
    else:
        instance._original_order_status = None # New order

@receiver(post_save, sender=Order)
def handle_order_status_changes(sender, instance, created, **kwargs):
    """
    Handle order status changes, including updating order item statuses to 'delivered'
    when the order is delivered, and sending notifications.
    """
    # Logic for initial order creation notifications
    if created:
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
                            title=f'New Order Received #{instance.order.order_number}',
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
            print(f"DEBUG: Unexpected error in handle_order_status_changes (creation): {e}")
            import traceback
            traceback.print_exc()
            # Don't raise the exception - let the order creation succeed

    # Logic for existing order status changes
    if not created and instance.pk: # Only for updates to existing orders
        try:
            # Check if order_status has actually changed using the original status from pre_save
            original_order_status = getattr(instance, '_original_order_status', None)
            
            if original_order_status != instance.order_status:
                # If order status changes to 'delivered', update all order items to 'delivered'
                if instance.order_status == 'delivered':
                    for item in instance.items.all():
                        if item.item_status != 'delivered':
                            item.item_status = 'delivered'
                            item.save(update_fields=['item_status']) # Save only the changed field
                    print(f"DEBUG: Order {instance.order_id} delivered. All order items marked as delivered.")
                
                # Send status update notifications (existing logic)
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
                                title=f'Order Update #{instance.order.order_number}',
                                message=status_messages[instance.order_status],
                                send_sms=instance.customer.sms_notifications
                            )
                except ImportError:
                    pass
        except Exception as e:
            print(f"DEBUG: Unexpected error in handle_order_status_changes (update): {e}")
            import traceback
            traceback.print_exc()
