from rest_framework import serializers
from .models import Payout
from users.models import User
from django.utils import timezone

class PayoutSerializer(serializers.ModelSerializer):
    """Serializer for the Payout model"""
    user_username = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Payout
        fields = [
            'payout_id', 'user', 'user_username', 'user_role', 'order',
            'amount', 'status', 'transaction_reference', 'payout_date',
            'processed_date', 'notes'
        ]
        read_only_fields = ['payout_id', 'payout_date']
    
    def get_user_username(self, obj):
        """Return the phone number of the user"""
        return obj.user.phone_number
    
    def get_user_role(self, obj):
        """Return the role of the user"""
        return obj.user.user_role
    
    def validate_user(self, value):
        """Validate that the user is a farmer or rider"""
        if value.user_role not in ['farmer', 'rider']:
            raise serializers.ValidationError("Payouts can only be made to farmers or riders.")
        return value
    
    def validate(self, data):
        """Additional validation for payouts"""
        # If status is being updated to 'processed', ensure a transaction reference is provided
        if 'status' in data and data['status'] == 'processed':
            if 'transaction_reference' not in data or not data['transaction_reference']:
                raise serializers.ValidationError({
                    'transaction_reference': "Transaction reference is required when processing a payout."
                })
            
            # Set the processed_date
            data['processed_date'] = timezone.now()
        
        # If status is being updated to 'failed', ensure notes are provided
        if 'status' in data and data['status'] == 'failed':
            if 'notes' not in data or not data['notes']:
                raise serializers.ValidationError({
                    'notes': "Notes explaining the failure reason are required when marking a payout as failed."
                })
        
        return data
