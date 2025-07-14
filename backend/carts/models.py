from django.db import models
from django.conf import settings
from products.models import ProductListing
from decimal import Decimal

class Cart(models.Model):
    """
    Model representing a customer's shopping cart.
    A customer can have at most one active cart.
    """
    cart_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.customer.get_full_name() or self.customer.phone_number}"
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def items_total(self):
        """Calculate total cost of all items in cart"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def items_count(self):
        """Get total number of items in cart"""
        return self.items.count()
    
    @property
    def total_quantity(self):
        """Get total quantity of all items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def calculate_delivery_fee(self, delivery_location=None):
        """Calculate delivery fee by using centralized Order calculation logic"""
        from orders.models import Order
        return Order.calculate_delivery_fee_for_cart(self.items.all(), delivery_location)
    
    @property
    def estimated_delivery_fee(self):
        """Get estimated delivery fee using customer's default location"""
        try:
            default_location = self.customer.locations.filter(is_default=True).first()
            return self.calculate_delivery_fee(default_location)
        except:
            return self.calculate_delivery_fee()
    
    @property
    def total_with_delivery(self):
        """Get total including estimated delivery fee"""
        return self.items_total + self.estimated_delivery_fee
    
    def get_farmers_summary(self):
        """Get summary of farmers and their items in this cart"""
        farmers = {}
        for item in self.items.select_related('listing__farmer').all():
            farmer_id = item.listing.farmer.user_id
            if farmer_id not in farmers:
                farmers[farmer_id] = {
                    'farmer': item.listing.farmer,
                    'items': [],
                    'subtotal': Decimal('0.00')
                }
            farmers[farmer_id]['items'].append(item)
            farmers[farmer_id]['subtotal'] += item.subtotal
        
        return list(farmers.values())
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()

class CartItem(models.Model):
    """
    Model representing an item in a customer's cart.
    Each cart item is associated with a product listing and has a quantity and price.
    """
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    listing = models.ForeignKey(
        ProductListing,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'listing')  # Prevent duplicate items in cart
        ordering = ['added_at']
    
    def __str__(self):
        return f"{self.quantity} of {self.listing.product.product_name} in {self.cart}"
    
    @property
    def subtotal(self):
        """
        Calculate the subtotal for this cart item (quantity * price_at_addition)
        """
        return self.quantity * self.price_at_addition
    
    @property
    def price_changed(self):
        """Check if the current listing price differs from price when added to cart"""
        return self.listing.current_price != self.price_at_addition
    
    @property
    def availability_status(self):
        """Check current availability of the listing"""
        if self.listing.listing_status != 'available':
            return f"Not available - {self.listing.get_listing_status_display()}"
        
        if self.listing.quantity_available < self.quantity:
            return f"Insufficient quantity - Only {self.listing.quantity_available} available"
        
        return "Available"
    
    def update_price_to_current(self):
        """Update the cart item price to current listing price"""
        self.price_at_addition = self.listing.current_price
        self.save()
    
    def save(self, *args, **kwargs):
        # Set price_at_addition to current listing price if not already set
        if not self.price_at_addition:
            self.price_at_addition = self.listing.current_price
        super().save(*args, **kwargs)
