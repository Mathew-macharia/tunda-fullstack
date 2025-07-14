from rest_framework import serializers
from .models import Notification, Message, SupportTicket, FAQ
from users.models import User
from orders.models import Order

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for the Notification model"""
    user_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'notification_id', 'user', 'user_username', 'notification_type',
            'title', 'message', 'is_read', 'send_sms', 'related_id', 'created_at'
        ]
        read_only_fields = ['notification_id', 'created_at']
    
    def get_user_username(self, obj):
        """Return the phone number of the user"""
        return obj.user.phone_number
    
    def validate(self, data):
        """Ensure only admin can create notifications for other users"""
        request = self.context.get('request')
        user = request.user if request else None
        
        if user and user.is_authenticated:
            # If the user is trying to create a notification for someone else
            if 'user' in data and data['user'] != user:
                # Only admin can create notifications for other users
                if user.user_role != 'admin':
                    raise serializers.ValidationError({
                        'user': "You can only create notifications for yourself."
                    })
        
        return data


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""
    sender_username = serializers.SerializerMethodField()
    recipient_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_username', 'recipient', 
            'recipient_username', 'order', 'message_text', 'message_type',
            'media_url', 'is_read', 'created_at'
        ]
        read_only_fields = ['message_id', 'sender', 'created_at']
    
    def get_sender_username(self, obj):
        """Return the phone number of the sender"""
        return obj.sender.phone_number
    
    def get_recipient_username(self, obj):
        """Return the phone number of the recipient"""
        return obj.recipient.phone_number
    
    def validate_recipient(self, value):
        """Validate that the recipient exists and is not the sender"""
        request = self.context.get('request')
        user = request.user if request else None
        
        if user and value == user:
            raise serializers.ValidationError("You cannot send a message to yourself.")
        
        # Check if recipient is an admin, farmer, rider, or customer
        if value.user_role not in ['admin', 'farmer', 'rider', 'customer']:
            raise serializers.ValidationError("Invalid recipient.")
        
        return value
    
    def validate_order(self, value):
        """Validate that the order exists and is related to the sender or recipient"""
        request = self.context.get('request')
        user = request.user if request else None
        
        if value and user:
            # For customers, check if the order belongs to them
            if user.user_role == 'customer' and value.customer != user:
                raise serializers.ValidationError("You can only send messages related to your own orders.")
            
            # For farmers, check if they have products in the order
            if user.user_role == 'farmer':
                # Check if any order item's product belongs to this farmer
                has_product = False
                for item in value.order_items.all():
                    if item.product.farm.farmer == user:
                        has_product = True
                        break
                        
                if not has_product:
                    raise serializers.ValidationError("You can only send messages related to orders containing your products.")
            
            # For riders, check if they are assigned to the delivery
            if user.user_role == 'rider' and not value.delivery_set.filter(rider=user).exists():
                raise serializers.ValidationError("You can only send messages related to deliveries assigned to you.")
        
        return value
    
    def create(self, validated_data):
        """Create a new message with the current user as sender"""
        request = self.context.get('request')
        user = request.user if request else None
        
        validated_data['sender'] = user
        return super().create(validated_data)


class SupportTicketSerializer(serializers.ModelSerializer):
    """Serializer for the SupportTicket model"""
    user_username = serializers.SerializerMethodField()
    assigned_to_username = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'ticket_id', 'user', 'user_username', 'order', 'ticket_number',
            'subject', 'description', 'category', 'priority', 'status',
            'assigned_to', 'assigned_to_username', 'resolution_notes',
            'created_at', 'resolved_at'
        ]
        read_only_fields = ['ticket_id', 'user', 'ticket_number', 'created_at', 'resolved_at']
    
    def get_user_username(self, obj):
        """Return the phone number of the user"""
        return obj.user.phone_number
    
    def get_assigned_to_username(self, obj):
        """Return the phone number of the assigned admin"""
        return obj.assigned_to.phone_number if obj.assigned_to else None
    
    def validate_order(self, value):
        """Validate that the order exists and belongs to the user"""
        request = self.context.get('request')
        user = request.user if request else None
        
        if value and user and user.user_role == 'customer':
            if value.customer != user:
                raise serializers.ValidationError("You can only create tickets for your own orders.")
        
        return value
    
    def validate(self, data):
        """Custom validation for support tickets"""
        request = self.context.get('request')
        user = request.user if request else None
        
        # For creation, user should be set to the authenticated user (unless admin)
        if self.instance is None:  # Create operation
            if user:
                # Always set the user field to the authenticated user for non-admin users
                if user.user_role != 'admin':
                    data['user'] = user
                # For admin users, if no user is specified, default to themselves
                elif 'user' not in data:
                    data['user'] = user
        
        # Only admins can update status, priority, assigned_to, and resolution_notes
        if self.instance and user and user.user_role != 'admin':
            for field in ['status', 'priority', 'assigned_to', 'resolution_notes']:
                if field in data and getattr(self.instance, field) != data[field]:
                    raise serializers.ValidationError({
                        field: f"Only admins can update the {field}."
                    })
        
        return data


class AdminTicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin updates to support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to', 'resolution_notes']
    
    def validate_assigned_to(self, value):
        """Validate that the assigned_to user is an admin"""
        if value and value.user_role != 'admin':
            raise serializers.ValidationError("Tickets can only be assigned to admin users.")
        return value


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for the FAQ model"""
    
    class Meta:
        model = FAQ
        fields = [
            'faq_id', 'question', 'answer', 'target_role', 'is_active',
            'order_index', 'created_at', 'updated_at'
        ]
        read_only_fields = ['faq_id', 'created_at', 'updated_at']
