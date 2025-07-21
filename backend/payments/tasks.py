from celery import shared_task
import logging
from django.db import transaction
from django.utils import timezone
from .models import PaymentTransaction, PaymentSession
from .services.mpesa_service import MpesaService
from .serializers import MpesaCallbackSerializer

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_mpesa_callback_task(self, callback_data):
    """
    Celery task to process M-Pesa callback data asynchronously.
    """
    try:
        logger.info(f"Processing M-Pesa callback in background task: {callback_data}")

        # Validate callback structure
        serializer = MpesaCallbackSerializer(data=callback_data)
        serializer.is_valid(raise_exception=True) # Raise exception if invalid

        # Process callback using M-Pesa service
        mpesa_service = MpesaService()
        callback_info = mpesa_service.process_callback(callback_data)

        checkout_request_id = callback_info['checkout_request_id']

        with transaction.atomic():
            # Find the transaction
            try:
                transaction_obj = PaymentTransaction.objects.select_for_update().get(
                    mpesa_checkout_request_id=checkout_request_id
                )
            except PaymentTransaction.DoesNotExist:
                logger.error(f"Transaction not found for checkout request: {checkout_request_id}. Retrying...")
                raise self.retry(exc=PaymentTransaction.DoesNotExist("Transaction not found"), countdown=60)

            # Prevent reprocessing if already completed
            if transaction_obj.payment_status == 'completed':
                logger.info(f"Transaction {transaction_obj.transaction_id} already completed. Skipping reprocessing.")
                return

            # Update transaction with callback data
            transaction_obj.callback_received = True
            transaction_obj.callback_data = callback_data

            result_code = callback_info['result_code']

            if result_code == 0:
                # Payment successful
                transaction_obj.payment_status = 'completed'
                transaction_obj.payment_date = timezone.now()
                transaction_obj.mpesa_receipt_number = callback_info['mpesa_receipt_number']
                transaction_obj.transaction_code = callback_info['mpesa_receipt_number']
                logger.info(f"Payment successful for transaction {transaction_obj.transaction_id}")
            else:
                # Payment failed
                transaction_obj.payment_status = 'failed'
                transaction_obj.failure_reason = callback_info['result_desc']
                logger.info(f"Payment failed for transaction {transaction_obj.transaction_id}: {callback_info['result_desc']}")

            transaction_obj.save()

            # Update payment status (handles both session and order-based flows)
            transaction_obj.update_payment_status()
            logger.info(f"Payment status updated for transaction {transaction_obj.transaction_id}")

    except Exception as e:
        logger.exception(f"Error processing M-Pesa callback in task: {e}")
        # Optionally retry the task on failure
        raise self.retry(exc=e, countdown=300) # Retry after 5 minutes
