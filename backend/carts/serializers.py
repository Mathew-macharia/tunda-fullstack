from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductListing
from products.serializers import ProductListingSerializer
from decimal import Decimal

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items with direct product listing details for display
    """
    product_name = serializers.CharField(source='listing.product.product_name', read_only=True)
    farm_name = serializers.CharField(source='listing.farm.farm_name', read_only=True)
    current_price = serializers.DecimalField(source='listing.current_price', max_digits=10, decimal_places=2, read_only=True)
    product_unit = serializers.CharField(source='listing.product.get_unit_of_measure_display', read_only=True)
    photos = serializers.JSONField(source='listing.photos', read_only=True)
    quantity_available = serializers.DecimalField(source='listing.quantity_available', max_digits=10, decimal_places=2, read_only=True)
    min_order_quantity = serializers.DecimalField(source='listing.min_order_quantity', max_digits=10, decimal_places=2, read_only=True)
    availability_status = serializers.CharField(source='listing.get_listing_status_display', read_only=True)
    price_changed = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'cart_item_id', 'cart', 'listing', 'quantity', 'price_at_addition', 'subtotal', 
            'added_at', 'updated_at', 'product_name', 'farm_name', 'current_price', 
            'product_unit', 'photos', 'quantity_available', 'min_order_quantity', 
            'availability_status', 'price_changed'
        ]
        read_only_fields = [
            'cart_item_id', 'cart', 'price_at_addition', 'added_at', 'updated_at',
            'product_name', 'farm_name', 'current_price', 'product_unit', 'photos',
            'quantity_available', 'min_order_quantity', 'availability_status', 'price_changed'
        ]
    
    def get_price_changed(self, obj):
        """
        Check if the current price of the listing has changed since it was added to the cart.
        """
        return obj.price_at_addition != obj.listing.current_price

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
    estimated_delivery_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_with_delivery = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'cart_id', 'customer', 'items', 'total_items', 'total_cost', 
            'estimated_delivery_fee', 'total_with_delivery', 'created_at', 'updated_at'
        ]
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
