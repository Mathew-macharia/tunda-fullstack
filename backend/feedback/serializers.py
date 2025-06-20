from rest_framework import serializers
from .models import Review
from orders.models import OrderItem
from users.models import User

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model"""
    reviewer_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'reviewer', 'reviewer_username', 'order_item', 
            'target_type', 'target_id', 'rating', 'comment', 
            'review_photos', 'is_verified_purchase', 'is_visible', 'review_date'
        ]
        read_only_fields = ['review_id', 'reviewer', 'is_verified_purchase', 'review_date']
    
    def get_reviewer_username(self, obj):
        """
        Return the phone number of the reviewer for admins.
        For other users, return initials from first_name and last_name, or 'A' if no name.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.user_role == 'admin':
            return obj.reviewer.phone_number
        
        # For non-admin users, generate initials
        first_name_initial = obj.reviewer.first_name[0].upper() if obj.reviewer.first_name else ''
        last_name_initial = obj.reviewer.last_name[0].upper() if obj.reviewer.last_name else ''
        
        if first_name_initial and last_name_initial:
            return f"{first_name_initial}{last_name_initial}"
        elif first_name_initial:
            return first_name_initial
        elif last_name_initial:
            return last_name_initial
        else:
            return 'A' # Default to 'A' if no name parts are available
    
    def validate(self, data):
        """
        Custom validation to ensure:
        1. User can only review completed orders
        2. The target_type and target_id are valid
        3. The user hasn't already reviewed this target from this order
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        # Check order_item belongs to the user and is delivered
        if 'order_item' in data and data['order_item']:
            order_item = data['order_item']
            
            # Verify the order item belongs to the user
            if order_item.order.customer != user:
                raise serializers.ValidationError({
                    'order_item': "You can only review items from your own orders."
                })
            
            # Verify the order is delivered
            if order_item.order.order_status != 'delivered':
                raise serializers.ValidationError({
                    'order_item': "You can only review items from delivered orders."
                })
            
            # Verify the user hasn't already reviewed this target from this order item
            # This check should only apply when creating a new review, not updating an existing one
            if not self.instance: # Only apply this validation if it's a creation (not an update)
                existing_review = Review.objects.filter(
                    reviewer=user,
                    order_item=order_item,
                    target_type=data['target_type'],
                    target_id=data['target_id']
                ).exists()
                
                if existing_review:
                    raise serializers.ValidationError({
                        'order_item': f"You've already reviewed this {data['target_type']} from this order."
                    })
            
            # Set verified purchase since it's linked to a valid order item
            data['is_verified_purchase'] = True
        else:
            # If no order_item, it's not a verified purchase
            data['is_verified_purchase'] = False
        
        return data
    
    def create(self, validated_data):
        """Create a new review with the current user as reviewer"""
        request = self.context.get('request')
        user = request.user if request else None
        
        validated_data['reviewer'] = user
        return super().create(validated_data)
