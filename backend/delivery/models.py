from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import User
from orders.models import Order

class Vehicle(models.Model):
    """Model representing a rider's vehicle"""
    VEHICLE_TYPES = (
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('tuk_tuk', 'Tuk Tuk'),
        ('pickup', 'Pickup'),
        ('van', 'Van'),
    )
    
    vehicle_id = models.AutoField(primary_key=True)
    rider = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vehicle')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    registration_number = models.CharField(max_length=50, unique=True)
    capacity_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validate that the rider has the 'rider' role"""
        if self.rider.user_role != 'rider':
            raise ValidationError({
                'rider': 'Only users with the role "rider" can have a vehicle.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.rider.get_full_name()}'s {self.get_vehicle_type_display()} ({self.registration_number})"

class Delivery(models.Model):
    """Model representing a delivery of an order"""
    DELIVERY_STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('on_the_way', 'On The Way'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    
    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending_pickup')
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validate that the rider has the 'rider' role and the order is confirmed"""
        if self.rider and self.rider.user_role != 'rider':
            raise ValidationError({
                'rider': 'Only users with the role "rider" can be assigned to deliveries.'
            })
        
        # Validate order status
        valid_order_statuses = ['confirmed', 'processing', 'out_for_delivery', 'delivered']
        if self.order.order_status not in valid_order_statuses:
            raise ValidationError({
                'order': f'Only orders with status {valid_order_statuses} can have deliveries.'
            })
        
        # Validate that the vehicle belongs to the rider
        if self.vehicle and self.rider and self.vehicle.rider != self.rider:
            raise ValidationError({
                'vehicle': 'The vehicle must belong to the assigned rider.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Set timestamps based on status changes
        if self.delivery_status == 'picked_up' and not self.pickup_time:
            self.pickup_time = timezone.now()
        elif self.delivery_status == 'delivered' and not self.delivery_time:
            self.delivery_time = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Delivery #{self.delivery_id} for Order #{self.order.order_number}"

class DeliveryRoute(models.Model):
    """Model representing a delivery route for a rider"""
    route_id = models.AutoField(primary_key=True)
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    route_name = models.CharField(max_length=100)
    route_locations = models.JSONField(help_text="Array of location IDs in order for route optimization")
    estimated_time_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validate that the rider has the 'rider' role"""
        if self.rider.user_role != 'rider':
            raise ValidationError({
                'rider': 'Only users with the role "rider" can have delivery routes.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.route_name} (Rider: {self.rider.get_full_name()})"

@receiver(post_save, sender=Delivery)
def update_order_status_on_delivery_update(sender, instance, **kwargs):
    """Update the order status when delivery status changes"""
    order = instance.order
    
    # Update order status based on delivery status
    if instance.delivery_status == 'picked_up' and order.order_status != 'processing':
        order.order_status = 'processing'
        order.save()
    elif instance.delivery_status == 'on_the_way' and order.order_status != 'out_for_delivery':
        order.order_status = 'out_for_delivery'
        order.save()
    elif instance.delivery_status == 'delivered' and order.order_status != 'delivered':
        order.order_status = 'delivered'
        # If payment type is Cash on Delivery, mark as paid
        if order.payment_method and order.payment_method.payment_type == 'CashOnDelivery' and order.payment_status != 'paid':
            order.payment_status = 'paid'
        # Update all order items to delivered
        order.items.update(item_status='delivered')
        order.save()
    elif instance.delivery_status == 'failed' and order.order_status != 'failed_delivery':
        order.order_status = 'failed_delivery'
        order.save()

# Store previous rider state for comparison
_previous_delivery_states = {}

@receiver(pre_save, sender=Delivery)
def store_previous_delivery_state(sender, instance, **kwargs):
    """Store the previous state of delivery before save"""
    if instance.pk:
        try:
            old_instance = Delivery.objects.get(pk=instance.pk)
            _previous_delivery_states[instance.pk] = {
                'rider': old_instance.rider,
                'delivery_status': old_instance.delivery_status
            }
        except Delivery.DoesNotExist:
            pass

@receiver(post_save, sender=Delivery)
def send_rider_assignment_notification(sender, instance, created, **kwargs):
    """Send notification to rider when they are assigned to a delivery"""
    try:
        from communication.models import Notification
        
        should_notify = False
        notification_message = ""
        
        if created and instance.rider:
            # New delivery with rider assigned
            should_notify = True
            notification_message = (
                f'You have been assigned to deliver Order #{instance.order.order_number}. '
                f'Total value: KES {instance.order.total_amount}. '
                f'Please check your delivery dashboard for details.'
            )
        elif not created and instance.pk in _previous_delivery_states:
            # Check if rider assignment changed
            previous_state = _previous_delivery_states[instance.pk]
            previous_rider = previous_state.get('rider')
            
            if previous_rider != instance.rider and instance.rider:
                # Rider was assigned or changed
                should_notify = True
                action = "reassigned" if previous_rider else "assigned"
                notification_message = (
                    f'You have been {action} to deliver Order #{instance.order.order_number}. '
                    f'Total value: KES {instance.order.total_amount}. '
                    f'Please check your delivery dashboard for details.'
                )
            
            # Clean up stored state
            del _previous_delivery_states[instance.pk]
        
        if should_notify and instance.rider.should_receive_notification('order_update'):
            # Get delivery address details
            delivery_location = "N/A"
            if instance.order.delivery_location:
                delivery_location = f"{instance.order.delivery_location.location_name}"
            
            full_message = f"{notification_message} Delivery to: {delivery_location}"
            
            Notification.objects.create(
                user=instance.rider,
                notification_type='order_update',
                title=f'Delivery Assignment #{instance.delivery_id}',
                message=full_message,
                send_sms=instance.rider.sms_notifications,
                related_id=instance.delivery_id
            )
            
    except ImportError:
        # Communication app not available
        pass
    except Exception as e:
        # Log error but don't break delivery creation
        print(f"Error sending rider notification: {e}")
        pass
