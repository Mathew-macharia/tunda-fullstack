from celery import shared_task
import logging
from communication.models import Notification
from users.models import User
from core.services.sms_service import SMSService
from django.apps import apps

logger = logging.getLogger(__name__)

@shared_task
def send_notification_task(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    send_sms: bool = False,
    related_id: str = None
):
    """
    Celery task to create a Notification record and optionally send an SMS.
    This task is called by the NotificationService to perform asynchronous dispatch.
    """
    try:
        User = apps.get_model('users', 'User')
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found for notification task.")
        return

    try:
        # Create the in-app notification record
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            send_sms=send_sms and user.sms_notifications, # Only store send_sms=True if user prefers SMS
            related_id=related_id
        )
        logger.info(f"Notification created for user {user.phone_number} (ID: {notification.notification_id}) via Celery task.")

        # Conditionally send SMS if requested and user prefers SMS
        if send_sms and user.sms_notifications:
            sms_service_instance = SMSService.get_instance() # Get the singleton instance
            sms_service_instance.send_sms(user.phone_number, message) # Call the instance method
            logger.info(f"SMS dispatched for user {user.phone_number} for notification type {notification_type} via Celery task.")
        
        # TODO: Add logic for email notifications here if user.email_notifications is True

    except Exception as e:
        logger.exception(f"Error in send_notification_task for user {user_id}: {e}")
