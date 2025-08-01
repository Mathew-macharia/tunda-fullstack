from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db import models

from .models import PaymentMethod, PaymentTransaction, PaymentSession
from .serializers import (
    PaymentMethodSerializer, PaymentMethodCreateUpdateSerializer,
    PaymentTransactionSerializer, PaymentTransactionCreateSerializer,
    PaymentCallbackSerializer, MpesaPaymentInitiateSerializer, MpesaCallbackSerializer,
    PaymentSessionSerializer, PaymentSessionCreateSerializer,
    PaymentSessionInitiatePaymentSerializer
)
from .tasks import process_mpesa_callback_task # NEW IMPORT


class IsCustomerUser(permissions.BasePermission):
    """
    Permission that allows access only to customer users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'customer'


class IsAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to admin users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'admin'


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment methods
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsCustomerUser]
    
    def get_queryset(self):
        """
        Return only the payment methods belonging to the current user
        """
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentMethodCreateUpdateSerializer
        return PaymentMethodSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set a payment method as the default for the user
        """
        payment_method = self.get_object()
        
        # Update all payment methods to not be default
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Set this payment method as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment transactions
    """
    serializer_class = PaymentTransactionSerializer
    
    
    def get_queryset(self):
        """
        Return only the payment transactions relevant to the current user
        Admin users can see all transactions
        """
        user = self.request.user
        if user.user_role == 'admin':
            return PaymentTransaction.objects.all()
        # Allow customers to see transactions linked to their orders OR their payment sessions
        return PaymentTransaction.objects.filter(
            models.Q(order__customer=user) | models.Q(payment_session__user=user)
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentTransactionCreateSerializer
        elif self.action == 'callback':
            return PaymentCallbackSerializer
        return PaymentTransactionSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def callback(self, request):
        """
        Handle payment callback from payment provider
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.update_transaction(serializer.validated_data)
            response_serializer = PaymentTransactionSerializer(transaction)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def simulate_payment(self, request, pk=None):
        """
        Simulate a successful payment for testing purposes
        """
        payment_transaction = self.get_object()
        
        # Only allow simulating pending transactions
        if payment_transaction.payment_status != 'pending':
            return Response(
                {'error': 'Can only simulate payment for pending transactions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update transaction to completed
        payment_transaction.payment_status = 'completed'
        payment_transaction.payment_date = timezone.now()
        payment_transaction.transaction_code = f'SIM-{timezone.now().timestamp()}'
        payment_transaction.save()
        
        # Update order status
        payment_transaction.update_order_status()
        
        serializer = self.get_serializer(payment_transaction)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def initiate_mpesa_payment(self, request):
        """
        Initiate M-Pesa STK Push payment for an order
        """
        from .services.mpesa_service import MpesaService
        from orders.models import Order
        
        serializer = MpesaPaymentInitiateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data['order_id']
        phone_number = serializer.validated_data['phone_number']
        
        try:
            # Get the order
            order = Order.objects.get(order_id=order_id, customer=request.user)
            
            # Get or create M-Pesa payment method
            payment_method, created = PaymentMethod.objects.get_or_create(
                user=request.user,
                payment_type='Mpesa',
                defaults={
                    'mpesa_phone': phone_number,
                    'is_default': False,
                    'is_active': True
                }
            )
            
            # Update phone number if it changed
            if payment_method.mpesa_phone != phone_number:
                payment_method.mpesa_phone = phone_number
                payment_method.save()
            
            # Create payment transaction
            transaction = PaymentTransaction.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                phone_number=phone_number
            )
            
            # Initialize M-Pesa service and initiate STK Push
            mpesa_service = MpesaService()
            mpesa_response = mpesa_service.initiate_stk_push(
                phone_number=phone_number,
                amount=order.total_amount,
                order_reference=order.order_number,
                description=f'Payment for order {order.order_number}'
            )
            
            # Check M-Pesa response
            response_code = mpesa_response.get('ResponseCode')
            if response_code == '0':
                # Success - update transaction with M-Pesa details
                transaction.mpesa_checkout_request_id = mpesa_response.get('CheckoutRequestID')
                transaction.mpesa_merchant_request_id = mpesa_response.get('MerchantRequestID')
                transaction.save()
                
                return Response({
                    'status': 'success',
                    'message': 'STK Push sent successfully. Please check your phone.',
                    'transaction_id': transaction.transaction_id,
                    'checkout_request_id': transaction.mpesa_checkout_request_id,
                    'customer_message': mpesa_response.get('CustomerMessage', 'Please check your phone for M-Pesa prompt.')
                }, status=status.HTTP_200_OK)
            else:
                # Failed - update transaction status
                transaction.payment_status = 'failed'
                transaction.failure_reason = mpesa_response.get('errorMessage', 'STK Push failed')
                transaction.save()
                
                return Response({
                    'status': 'error',
                    'message': mpesa_response.get('errorMessage', 'Failed to initiate payment'),
                    'error_code': response_code
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[], authentication_classes=[])
    @csrf_exempt
    def mpesa_callback(self, request):
        """
        Handle M-Pesa STK Push callback.
        Immediately returns 200 OK and processes asynchronously using Celery.
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Log the raw callback for debugging
            logger.info(f"M-Pesa callback received: {request.data}")

            # Immediately return 200 OK to Daraja
            # The actual processing will happen in a background task
            process_mpesa_callback_task.delay(request.data) # Dispatch task asynchronously

            return Response({
                'status': 'success',
                'message': 'Callback received and processing initiated'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error receiving M-Pesa callback or dispatching task: {str(e)}")
            # Even if there's an error dispatching, we still try to return 200 to Daraja
            return Response({
                'status': 'error',
                'message': 'Failed to process callback internally'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def check_mpesa_status(self, request, pk=None):
        """
        Check M-Pesa transaction status by querying M-Pesa API
        """
        from .services.mpesa_service import MpesaService
        
        transaction = self.get_object()
        
        if not transaction.mpesa_checkout_request_id:
            return Response({
                'error': 'This is not an M-Pesa transaction'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mpesa_service = MpesaService()
            status_response = mpesa_service.query_transaction_status(
                transaction.mpesa_checkout_request_id
            )
            
            # Update transaction if status has changed
            result_code = status_response.get('ResultCode')
            if result_code == '0' and transaction.payment_status == 'pending':
                transaction.payment_status = 'completed'
                transaction.payment_date = timezone.now()
                transaction.save()
                transaction.update_order_status()
            elif result_code != '0' and transaction.payment_status == 'pending':
                transaction.payment_status = 'failed'
                transaction.failure_reason = status_response.get('ResultDesc', 'Payment failed')
                transaction.save()
                transaction.update_order_status()
            
            serializer = self.get_serializer(transaction)
            return Response({
                'transaction': serializer.data,
                'mpesa_status': status_response
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to check status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment sessions (new payment-first approach)
    """
    serializer_class = PaymentSessionSerializer
    permission_classes = [IsCustomerUser]
    
    def get_queryset(self):
        """
        Return only the payment sessions belonging to the current user
        """
        return PaymentSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentSessionCreateSerializer
        elif self.action == 'initiate_payment':
            return PaymentSessionInitiatePaymentSerializer
        return PaymentSessionSerializer
    
    def perform_create(self, serializer):
        """
        Create payment session from user's cart.
        For serializers.Serializer, save() returns the created object, so we return it.
        """
        return serializer.save() # <--- MODIFIED: Ensure the created instance is returned

    # OVERRIDE: Ensure the created instance's data is returned
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use PaymentSessionCreateSerializer for input validation
        input_serializer = self.get_serializer(data=request.data) 
        input_serializer.is_valid(raise_exception=True)
        
        # Perform creation, capturing the instance returned by perform_create
        instance = self.perform_create(input_serializer) 
        
        # Use PaymentSessionSerializer (the one with session_id) for output
        response_data = PaymentSessionSerializer(instance).data # <--- MODIFIED LINE
        
        # TEMPORARY: Print the response data to the console
        print("DEBUG: Response data from PaymentSessionViewSet.create:", response_data)
        
        headers = self.get_success_headers(input_serializer.data) 
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """
        Initiate M-Pesa payment for a payment session
        """
        from .services.mpesa_service import MpesaService
        
        session = self.get_object()
        
        # Check session is valid
        if session.session_status not in ['pending', 'payment_initiated']:
            return Response({
                'error': 'Session is not in a valid state for payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if session.is_expired():
            session.session_status = 'expired'
            session.save()
            return Response({
                'error': 'Session has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get phone number (use session phone or override)
        phone_number = serializer.validated_data.get('phone_number', session.phone_number)
        
        try:
            # Get or create M-Pesa payment method
            payment_method, created = PaymentMethod.objects.get_or_create(
                user=request.user,
                payment_type='Mpesa',
                defaults={
                    'mpesa_phone': phone_number,
                    'is_default': False,
                    'is_active': True
                }
            )
            
            # Update phone number if it changed
            if payment_method.mpesa_phone != phone_number:
                payment_method.mpesa_phone = phone_number
                payment_method.save()
            
            # Create payment transaction linked to session
            transaction_obj = PaymentTransaction.objects.create(
                payment_session=session,
                payment_method=payment_method,
                amount=session.total_amount,
                phone_number=phone_number
            )
            
            # Initialize M-Pesa service and initiate STK Push
            mpesa_service = MpesaService()
            mpesa_response = mpesa_service.initiate_stk_push(
                phone_number=phone_number,
                amount=session.total_amount,
                reference=str(session.session_id),
                reference_type='session',
                description=f'Payment for session {session.session_id}'
            )
            
            # Check M-Pesa response
            response_code = mpesa_response.get('ResponseCode')
            if response_code == '0':
                # Success - update transaction and session
                transaction_obj.mpesa_checkout_request_id = mpesa_response.get('CheckoutRequestID')
                transaction_obj.mpesa_merchant_request_id = mpesa_response.get('MerchantRequestID')
                transaction_obj.save()
                
                session.session_status = 'payment_initiated'
                session.extend_expiry(15)  # Extend session by 15 minutes
                session.save()
                
                return Response({
                    'status': 'success',
                    'message': 'STK Push sent successfully. Please check your phone.',
                    'session_id': str(session.session_id),
                    'transaction_id': transaction_obj.transaction_id,
                    'checkout_request_id': transaction_obj.mpesa_checkout_request_id,
                    'customer_message': mpesa_response.get('CustomerMessage', 'Please check your phone for M-Pesa prompt.')
                }, status=status.HTTP_200_OK)
            else:
                # Failed - update transaction status
                transaction_obj.payment_status = 'failed'
                transaction_obj.failure_reason = mpesa_response.get('errorMessage', 'STK Push failed')
                transaction_obj.save()
                
                session.session_status = 'failed'
                session.save()
                
                return Response({
                    'status': 'error',
                    'message': mpesa_response.get('errorMessage', 'Failed to initiate payment'),
                    'error_code': response_code
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Check payment session status
        """
        session = self.get_object()
        
        # Check if session expired
        if session.is_expired() and session.session_status in ['pending', 'payment_initiated']:
            session.session_status = 'expired'
            session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def extend_session(self, request, pk=None):
        """
        Extend session expiry time
        """
        session = self.get_object()
        
        if session.session_status in ['pending', 'payment_initiated']:
            session.extend_expiry(15)
            return Response({
                'status': 'success',
                'message': 'Session extended',
                'expires_at': session.expires_at
            })
        else:
            return Response({
                'error': 'Cannot extend session in current state'
            }, status=status.HTTP_400_BAD_REQUEST)
