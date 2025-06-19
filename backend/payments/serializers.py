from rest_framework import serializers
from django.utils import timezone
from .models import PaymentMethod, PaymentTransaction
from orders.models import Order
from orders.serializers import OrderSerializer

class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving payment method details
    """
    class Meta:
        model = PaymentMethod
        fields = [
            'payment_method_id', 'payment_type', 'mpesa_phone',
            'is_default', 'is_active', 'created_at'
        ]
        read_only_fields = ['payment_method_id', 'created_at']
    
    def to_representation(self, instance):
        """
        Customize representation to include readable payment type
        """
        data = super().to_representation(instance)
        data['payment_type_display'] = instance.get_payment_type_display()
        return data

class PaymentMethodCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating or updating payment methods
    """
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'mpesa_phone', 'is_default', 'is_active']
    
    def validate(self, data):
        """
        Validate that M-Pesa phone number is provided for M-Pesa payment method
        """
        payment_type = data.get('payment_type')
        mpesa_phone = data.get('mpesa_phone')
        
        if payment_type == 'Mpesa' and not mpesa_phone:
            raise serializers.ValidationError({
                "mpesa_phone": "Phone number is required for M-Pesa payment method."
            })
            
        return data
    
    def create(self, validated_data):
        """
        Create a new payment method for the authenticated user
        """
        user = self.context['request'].user
        payment_method = PaymentMethod.objects.create(
            user=user,
            **validated_data
        )
        return payment_method

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving payment transaction details
    """
    order_details = OrderSerializer(source='order', read_only=True)
    payment_method_details = PaymentMethodSerializer(source='payment_method', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'transaction_id', 'order', 'payment_method', 'amount',
            'transaction_code', 'payment_status', 'payment_date',
            'failure_reason', 'created_at', 'order_details',
            'payment_method_details'
        ]
        read_only_fields = [
            'transaction_id', 'created_at', 'payment_date',
            'order_details', 'payment_method_details'
        ]

class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a payment transaction
    """
    class Meta:
        model = PaymentTransaction
        fields = ['order', 'payment_method', 'amount']
    
    def validate(self, data):
        """
        Validate payment transaction data
        """
        order = data.get('order')
        amount = data.get('amount')
        
        # Ensure the order belongs to the current user
        user = self.context['request'].user
        if order.customer != user:
            raise serializers.ValidationError({
                "order": "You can only create payment transactions for your own orders."
            })
        
        # Validate payment amount matches order amount
        total_order_amount = order.total_amount + order.delivery_fee
        if amount != total_order_amount:
            raise serializers.ValidationError({
                "amount": f"Payment amount ({amount}) must match the order total ({total_order_amount})."
            })
            
        return data
    
    def create(self, validated_data):
        """
        Create a new payment transaction
        """
        transaction = PaymentTransaction.objects.create(**validated_data)
        return transaction

class PaymentCallbackSerializer(serializers.Serializer):
    """
    Serializer for handling payment callbacks from payment providers
    """
    transaction_id = serializers.IntegerField(required=True)
    transaction_code = serializers.CharField(required=True)
    payment_status = serializers.ChoiceField(
        choices=PaymentTransaction.PAYMENT_STATUS_CHOICES,
        required=True
    )
    failure_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validate the payment callback data
        """
        transaction_id = data.get('transaction_id')
        
        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            raise serializers.ValidationError({
                "transaction_id": "Payment transaction not found."
            })
            
        if transaction.payment_status == 'completed':
            raise serializers.ValidationError({
                "transaction_id": "Payment has already been completed."
            })
            
        return {
            'transaction': transaction,
            **data
        }
    
    def update_transaction(self, validated_data):
        """
        Update the payment transaction with the callback data
        """
        transaction = validated_data.get('transaction')
        transaction_code = validated_data.get('transaction_code')
        payment_status = validated_data.get('payment_status')
        failure_reason = validated_data.get('failure_reason', '')
        
        transaction.transaction_code = transaction_code
        transaction.payment_status = payment_status
        
        if payment_status == 'completed':
            transaction.payment_date = timezone.now()
        elif payment_status == 'failed':
            transaction.failure_reason = failure_reason or 'No reason provided by payment provider'
            
        transaction.save()
        
        # Update the associated order
        transaction.update_order_status()
        
        return transaction
