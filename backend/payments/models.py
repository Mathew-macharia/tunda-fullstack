from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import uuid
from orders.models import Order
from delivery.models import Delivery

class PaymentSession(models.Model):
    """
    Payment session model to handle payment-first approach
    Stores cart snapshot and creates order only after successful payment
    """
    SESSION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('payment_initiated', 'Payment Initiated'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
        ('order_created', 'Order Created'),
    ]
    
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_sessions')
    cart_snapshot = models.JSONField(help_text="Complete cart data at time of payment")
    delivery_details = models.JSONField(help_text="Address, phone, instructions, etc.")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    session_status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='pending')
    
    # Links to created order (after payment success)
    order = models.OneToOneField(Order, null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_session')
    
    # Session management
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Session expires 15 minutes after creation")
    
    class Meta:
        db_table = 'Payment_Sessions'
        verbose_name = 'Payment Session'
        verbose_name_plural = 'Payment Sessions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment Session {self.session_id} - {self.user.phone_number} - {self.session_status}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if session has expired"""
        return timezone.now() > self.expires_at
    
    def extend_expiry(self, minutes=15):
        """Extend session expiry time"""
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save()
    
    def create_order_from_session(self):
        """Create order from successful payment session"""
        from orders.models import Order, OrderItem
        from locations.models import Location, UserAddress, County, SubCounty
        from products.models import ProductListing
        from carts.models import CartItem
        from django.db import transaction
        from django.core.exceptions import ValidationError
        
        if self.session_status != 'paid':
            raise ValidationError("Can only create order from paid sessions")
        
        if self.order:
            return self.order  # Order already created
        
        with transaction.atomic():
            # 1. Create delivery location from session data
            delivery_data = self.delivery_details
            
            # Get county and subcounty
            county = County.objects.get(county_id=delivery_data['county_id'])
            subcounty = SubCounty.objects.get(sub_county_id=delivery_data['subcounty_id'])
            
            # Create UserAddress
            user_address = UserAddress.objects.create(
                user=self.user,
                full_name=delivery_data['full_name'],
                phone_number=delivery_data['phone_number'],
                county=county,
                sub_county=subcounty,
                location_name=f"{subcounty.sub_county_name}, {county.county_name}",
                detailed_address=delivery_data['detailed_address']
            )
            
            # Create corresponding Location (for backward compatibility)
            delivery_location = Location.objects.create(
                user=self.user,
                location_name=user_address.location_name,
                sub_location=user_address.detailed_address,
                latitude=Decimal('0.0'),
                longitude=Decimal('0.0'),
                is_default=False
            )
            
            # 2. Get or create payment method
            payment_method, _ = PaymentMethod.objects.get_or_create(
                user=self.user,
                payment_type='Mpesa',
                defaults={
                    'mpesa_phone': self.phone_number,
                    'is_default': False,
                    'is_active': True
                }
            )
            
            # Update phone number if it changed
            if payment_method.mpesa_phone != self.phone_number:
                payment_method.mpesa_phone = self.phone_number
                payment_method.save()
            
            # 3. Create order with 'confirmed' status (payment already completed)
            order = Order.objects.create(
                customer=self.user,
                delivery_location=delivery_location,
                payment_method=payment_method,
                total_amount=self.total_amount,
                delivery_fee=self.delivery_fee,
                order_status='confirmed',  # Skip pending_payment
                payment_status='paid',     # Payment already completed
                estimated_delivery_date=delivery_data.get('estimated_delivery_date'),
                delivery_time_slot=delivery_data.get('delivery_time_slot'),
                special_instructions=delivery_data.get('special_instructions')
            )
            
            # 4. Create order items and update inventory
            for cart_item_data in self.cart_snapshot['items']:
                listing = ProductListing.objects.get(listing_id=cart_item_data['listing_id'])
                
                # Verify inventory is still available
                if cart_item_data['quantity'] > listing.quantity_available:
                    raise ValidationError(
                        f"Insufficient stock for {listing.product.product_name}. "
                        f"Available: {listing.quantity_available}, Requested: {cart_item_data['quantity']}"
                    )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    listing=listing,
                    farmer=listing.farm.farmer,
                    quantity=Decimal(str(cart_item_data['quantity'])), # Ensure quantity is Decimal
                    price_at_purchase=Decimal(str(cart_item_data['price_at_addition'])), # Ensure price is Decimal
                    total_price=Decimal(str(cart_item_data['quantity'])) * Decimal(str(cart_item_data['price_at_addition'])) # Ensure calculation uses Decimals
                )
                
                # Update inventory
                listing.quantity_available -= Decimal(str(cart_item_data['quantity'])) # Convert float to Decimal
                listing.save()
            
            # 5. Clear customer's cart
            CartItem.objects.filter(cart__customer=self.user).delete()
            
            # 6. Update session
            self.order = order
            self.session_status = 'order_created'
            self.save()
            
            # 7. Create Delivery record
            # The rider field is null=True, blank=True, so it can be created without a rider
            Delivery.objects.create(order=order)
            print(f"DEBUG: Delivery record created for Order {order.order_id} from PaymentSession.")
            
            return order

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
    Now supports both session-based (new) and order-based (legacy) flows
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4) # Changed from AutoField to UUIDField
    
    # NEW: Link to payment session (primary relationship for new flow)
    payment_session = models.ForeignKey(PaymentSession, null=True, blank=True, on_delete=models.CASCADE, related_name='transactions')
    
    # MODIFIED: Order becomes optional (populated after order creation)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE, related_name='payment_transactions')
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # M-Pesa specific fields
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    callback_received = models.BooleanField(default=False)
    callback_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        db_table = 'Payment_Transactions'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['payment_session']),
            models.Index(fields=['order']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['mpesa_checkout_request_id']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} - {self.payment_status}"
    
    def clean(self):
        """Ensure transaction is linked to either session or order"""
        from django.core.exceptions import ValidationError
        if not self.payment_session and not self.order:
            raise ValidationError("Transaction must be linked to either a payment session or an order")
    
    def update_payment_status(self):
        """
        Updated method to handle both session-based and order-based payments
        """
        if self.payment_status == 'completed':
            if self.payment_session:
                # NEW: Session-based flow
                self.payment_session.session_status = 'paid'
                self.payment_session.save()
                
                # Create order from session
                try:
                    order = self.payment_session.create_order_from_session()
                    
                    # Link transaction to created order
                    self.order = order
                    self.save()
                    
                except Exception as e:
                    # If order creation fails, mark session as failed
                    self.payment_session.session_status = 'failed'
                    self.payment_session.save()
                    self.payment_status = 'failed'
                    self.failure_reason = f"Order creation failed: {str(e)}"
                    self.save()
                    raise
                    
            elif self.order:
                # LEGACY: Order-based flow (for backward compatibility)
                self.order.payment_status = 'paid'
                if self.order.order_status == 'pending_payment':
                    self.order.order_status = 'confirmed'
                self.order.save()
                
        elif self.payment_status == 'failed':
            if self.payment_session:
                self.payment_session.session_status = 'failed'
                self.payment_session.save()
            elif self.order:
                self.order.payment_status = 'failed'
                self.order.save()
                
        elif self.payment_status == 'cancelled':
            if self.payment_session:
                self.payment_session.session_status = 'failed'
                self.payment_session.save()
            elif self.order:
                self.order.session_status = 'failed'
                self.order.save()
    
    # Keep the old method for backward compatibility
    def update_order_status(self):
        """Legacy method - calls the new update_payment_status method"""
        self.update_payment_status()
