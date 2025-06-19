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
        """Return the phone number of the reviewer"""
        return obj.reviewer.phone_number
    
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
