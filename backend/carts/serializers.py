from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductListing
from products.serializers import ProductListingSerializer
from decimal import Decimal

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items with nested product listing details
    """
    listing_details = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'cart_item_id', 'cart', 'listing', 'listing_details', 'quantity', 
            'price_at_addition', 'subtotal', 'added_at', 'updated_at'
        ]
        read_only_fields = ['cart_item_id', 'cart', 'price_at_addition', 'added_at', 'updated_at']
    
    def get_listing_details(self, obj):
        """
        Get detailed information about the product listing
        """
        from products.serializers import ProductListingSerializer
        return ProductListingSerializer(obj.listing, context=self.context).data
    
    def validate_listing(self, value):
        """
        Validate that the listing is available and active
        """
        if value.listing_status not in ['available', 'pre_order']:
            raise serializers.ValidationError("This product is not currently available for purchase.")
        return value
    
    def validate_quantity(self, value):
        """
        Validate that quantity is positive and not zero
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, data):
        """
        Validate that quantity does not exceed available stock
        """
        listing = data.get('listing')
        quantity = data.get('quantity')
        
        # Skip validation if listing or quantity is not provided (partial update)
        if not listing or not quantity:
            return data
            
        # Check if quantity exceeds available stock
        if quantity > listing.quantity_available:
            raise serializers.ValidationError({
                "quantity": f"Cannot add {quantity} items to cart. Only {listing.quantity_available} available."
            })
            
        # Check minimum order quantity
        if quantity < listing.min_order_quantity:
            raise serializers.ValidationError({
                "quantity": f"Minimum order quantity is {listing.min_order_quantity}."
            })
            
        return data
    
    def create(self, validated_data):
        """
        Create a new cart item with the current price of the listing
        """
        # Set price_at_addition to the current price of the listing
        validated_data['price_at_addition'] = validated_data['listing'].current_price
        
        # Make sure cart_id is properly set
        if 'cart' in validated_data and validated_data['cart'] is not None:
            # We're good, cart is already set properly
            pass
        elif 'cart_id' in self.context:
            # Set cart from context if available
            from .models import Cart
            validated_data['cart'] = Cart.objects.get(cart_id=self.context['cart_id'])
            
        return super().create(validated_data)

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for customer shopping carts with nested items
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['cart_id', 'customer', 'items', 'total_items', 'total_cost', 'created_at', 'updated_at']
        read_only_fields = ['cart_id', 'customer', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """
        Get the total number of items in the cart
        """
        return sum(item.quantity for item in obj.items.all())
    
    def get_total_cost(self, obj):
        """
        Calculate the total cost of all items in the cart
        """
        return sum(item.quantity * item.price_at_addition for item in obj.items.all())

class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to a cart
    """
    listing_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_listing_id(self, value):
        """
        Validate that the listing exists
        """
        try:
            listing = ProductListing.objects.get(listing_id=value)
        except ProductListing.DoesNotExist:
            raise serializers.ValidationError("Product listing not found.")
            
        if listing.listing_status not in ['available', 'pre_order']:
            raise serializers.ValidationError("This product is not currently available for purchase.")
            
        return value
    
    def validate_quantity(self, value):
        """
        Validate that quantity is positive and not zero
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, data):
        """
        Validate that quantity does not exceed available stock
        """
        listing_id = data.get('listing_id')
        quantity = data.get('quantity')
        
        try:
            listing = ProductListing.objects.get(listing_id=listing_id)
        except ProductListing.DoesNotExist:
            # Already validated in validate_listing_id
            return data
            
        # Check if quantity exceeds available stock
        if quantity > listing.quantity_available:
            raise serializers.ValidationError({
                "quantity": f"Cannot add {quantity} items to cart. Only {listing.quantity_available} available."
            })
            
        # Check minimum order quantity
        if quantity < listing.min_order_quantity:
            raise serializers.ValidationError({
                "quantity": f"Minimum order quantity is {listing.min_order_quantity}."
            })
            
        return data
