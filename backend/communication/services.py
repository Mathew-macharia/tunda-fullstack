import logging
from django.conf import settings
import logging
from communication.models import Notification
from users.models import User
from core.services.sms_service import SMSService
from communication.tasks import send_notification_task # Import the Celery task

logger = logging.getLogger(__name__)

class NotificationService:
    """
    A centralized service for creating and dispatching various types of notifications.
    Handles creation of Notification objects in the database and dispatches SMS.
    """

    @staticmethod
    def send_notification(
        user: User,
        notification_type: str,
        title: str,
        message: str,
        send_sms: bool = False,
        related_id: str = None, # UUID string
        **kwargs # For future expansion, e.g., email content, push data
    ) -> None: # Changed return type to None as task is async
        """
        Dispatches a Celery task to create a Notification record and optionally send an SMS.
        This method does not return the Notification object directly as it's asynchronous.

        Args:
            user (User): The recipient user.
            notification_type (str): Type of notification (e.g., 'order_update', 'payment_received').
            title (str): The title of the notification.
            message (str): The full message content.
            send_sms (bool): Whether to attempt sending an SMS.
            related_id (str, optional): UUID of a related object (e.g., Order ID, Delivery ID). Defaults to None.
        """
        if not user:
            logger.error("Attempted to send notification without a recipient user.")
            return

        try:
            # Dispatch the notification creation and SMS sending to a Celery task
            send_notification_task.delay(
                user_id=user.user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                send_sms=send_sms,
                related_id=str(related_id) if related_id else None # Ensure UUID is stringified for Celery
            )
            logger.info(f"Notification task dispatched for user {user.phone_number} for type {notification_type}.")

        except Exception as e:
            logger.exception(f"Error dispatching notification task for user {user.phone_number}: {e}")
