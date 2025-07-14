from rest_framework import serializers
from django.utils import timezone
from .models import PaymentMethod, PaymentTransaction, PaymentSession
from orders.models import Order
from orders.serializers import OrderSerializer
from carts.models import Cart, CartItem
from locations.models import County, SubCounty

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
            'payment_method_details', 'mpesa_checkout_request_id',
            'mpesa_merchant_request_id', 'mpesa_receipt_number',
            'phone_number', 'callback_received'
        ]
        read_only_fields = [
            'transaction_id', 'created_at', 'payment_date',
            'order_details', 'payment_method_details',
            'mpesa_checkout_request_id', 'mpesa_merchant_request_id',
            'mpesa_receipt_number', 'phone_number', 'callback_received'
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


class PaymentSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving payment session details
    """
    order_details = OrderSerializer(source='order', read_only=True)
    
    class Meta:
        model = PaymentSession
        fields = [
            'session_id', 'user', 'cart_snapshot', 'delivery_details',
            'total_amount', 'delivery_fee', 'phone_number', 'session_status',
            'order', 'order_details', 'created_at', 'expires_at'
        ]
        read_only_fields = [
            'session_id', 'user', 'created_at', 'expires_at', 'order', 'order_details'
        ]


class PaymentSessionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a payment session from cart
    """
    delivery_details = serializers.DictField()
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    delivery_time_slot = serializers.CharField(required=False, allow_blank=True)
    estimated_delivery_date = serializers.DateField(required=False, allow_null=True)
    
    def validate_delivery_details(self, value):
        """Validate delivery details structure"""
        required_fields = ['full_name', 'phone_number', 'county_id', 'subcounty_id', 'detailed_address']
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        # Validate county and subcounty exist
        try:
            County.objects.get(county_id=value['county_id'])
            SubCounty.objects.get(sub_county_id=value['subcounty_id'])
        except (County.DoesNotExist, SubCounty.DoesNotExist):
            raise serializers.ValidationError("Invalid county or subcounty")
        
        return value
    
    def validate(self, data):
        """Validate cart is not empty and calculate totals"""
        user = self.context['request'].user
        
        # Check cart is not empty
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("User does not have an active cart.")
            
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty")
        
        return data
    
    def create(self, validated_data):
        """Create payment session from cart"""
        from decimal import Decimal
        
        user = self.context['request'].user
        
        # Get current cart
        try:
            cart = Cart.objects.get(customer=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("User does not have an active cart.")
            
        cart_items = cart.items.all().select_related('listing__product', 'listing__farm')
        
        # Create cart snapshot
        cart_snapshot = {
            'items': [],
            'total_items': 0,
            'total_cost': Decimal('0.00'),
            'created_at': timezone.now().isoformat()
        }
        
        total_cost = Decimal('0.00')
        total_items = 0
        
        for item in cart_items:
            item_total = item.quantity * item.price_at_addition
            total_cost += item_total
            total_items += int(item.quantity)
            
            cart_snapshot['items'].append({
                'cart_item_id': item.cart_item_id,
                'listing_id': item.listing.listing_id,
                'product_name': item.listing.product.product_name,
                'farm_name': item.listing.farm.farm_name,
                'quantity': float(item.quantity),
                'price_at_addition': float(item.price_at_addition),
                'subtotal': float(item_total),
                'unit_of_measure': item.listing.product.unit_of_measure
            })
        
        cart_snapshot['total_items'] = total_items
        cart_snapshot['total_cost'] = float(total_cost)
        
        # Estimate delivery fee (simplified for now)
        delivery_fee = Decimal('50.00')  # Default delivery fee
        
        # Prepare delivery details
        delivery_details = {
            **validated_data['delivery_details'],
            'special_instructions': validated_data.get('special_instructions', ''),
            'delivery_time_slot': validated_data.get('delivery_time_slot'),
            'estimated_delivery_date': validated_data.get('estimated_delivery_date').isoformat() if validated_data.get('estimated_delivery_date') else None
        }
        
        # Create payment session
        session = PaymentSession.objects.create(
            user=user,
            cart_snapshot=cart_snapshot,
            delivery_details=delivery_details,
            total_amount=total_cost + delivery_fee,
            delivery_fee=delivery_fee,
            phone_number=validated_data['delivery_details']['phone_number']
        )
        
        return session


class PaymentSessionInitiatePaymentSerializer(serializers.Serializer):
    """
    Serializer for initiating payment for a session
    """
    phone_number = serializers.CharField(max_length=15, required=False)
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, value))
            
            # Check if it's a valid Kenyan phone number
            if not (phone.startswith('254') or phone.startswith('0') or len(phone) == 9):
                raise serializers.ValidationError("Invalid phone number format. Use format: 0712345678 or 254712345678")
        
        return value


class MpesaPaymentInitiateSerializer(serializers.Serializer):
    """
    Serializer for initiating M-Pesa STK Push payments
    """
    order_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15)
    
    def validate_order_id(self, value):
        """Validate that the order exists and belongs to the user"""
        user = self.context['request'].user
        try:
            order = Order.objects.get(order_id=value, customer=user)
            if order.payment_status == 'paid':
                raise serializers.ValidationError("This order has already been paid.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found or doesn't belong to you.")
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Kenyan phone number
        if not (phone.startswith('254') or phone.startswith('0') or len(phone) == 9):
            raise serializers.ValidationError("Invalid phone number format. Use format: 0712345678 or 254712345678")
        
        return value


class MpesaCallbackSerializer(serializers.Serializer):
    """
    Serializer for handling M-Pesa callback data
    """
    Body = serializers.DictField()
    
    def validate(self, data):
        """Validate M-Pesa callback structure"""
        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        if not stk_callback:
            raise serializers.ValidationError("Invalid M-Pesa callback format")
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        if not checkout_request_id:
            raise serializers.ValidationError("Missing CheckoutRequestID in callback")
        
        return data

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
