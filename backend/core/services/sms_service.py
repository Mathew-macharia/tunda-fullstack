import logging
from django.conf import settings
import africastalking
import certifi # Import certifi
import requests # Import requests

logger = logging.getLogger(__name__)

class SMSService:
    """
    A service for sending SMS notifications using Africa's Talking.
    """

    def __init__(self):
        # Initialize Africa's Talking SDK
        username = settings.AFRICASTALKING_USERNAME
        api_key = settings.AFRICASTALKING_API_KEY

        if not username or not api_key:
            logger.error("Africa's Talking credentials not configured. SMS sending will be disabled.")
            self.is_configured = False
        else:
            # Initialize Africa's Talking with explicit SSL verification
            # This is a workaround for SSL issues on some systems
            # Note: The africastalking library might not expose a direct way to pass 'verify'
            # to its internal requests calls. If this doesn't work, we might need to
            # fork the library or use a global environment variable.
            
            # Let's try to set the global verify path for requests, which africastalking uses
            # This is a less intrusive way than modifying africastalking's internal session.
            # This relies on requests picking up the global setting.
            requests.utils.DEFAULT_CA_BUNDLE_PATH = certifi.where()
            
            africastalking.initialize(username, api_key)
            self.sms = africastalking.SMS
            self.is_configured = True

    @staticmethod
    def get_instance():
        """
        Returns a singleton instance of SMSService.
        """
        if not hasattr(SMSService, '_instance'):
            SMSService._instance = SMSService()
        return SMSService._instance

    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Sends an SMS message to the specified phone number using Africa's Talking.

        Args:
            to_number (str): The recipient's phone number (e.g., '+254712345678').
            message (str): The content of the SMS message.

        Returns:
            bool: True if the SMS was sent successfully, False otherwise.
        """
        if not self.is_configured:
            logger.warning(f"SMS not sent to {to_number}: Africa's Talking not configured.")
            return False

        if not to_number or not message:
            logger.warning("Attempted to send SMS with missing recipient number or message.")
            return False

        try:
            # Africa's Talking expects a list of recipients
            recipients = [to_number]
            
            # Send the SMS
            # The 'verify' parameter is implicitly handled by requests.utils.DEFAULT_CA_BUNDLE_PATH
            response = self.sms.send(message, recipients)
            
            # Check the response from Africa's Talking
            if response and response['SMSMessageData']['Recipients'][0]['status'] == 'Success':
                logger.info(f"SMS sent successfully to {to_number}: '{message[:50]}...'")
                return True
            else:
                error_message = response['SMSMessageData']['Recipients'][0]['errorMessage'] if response else 'Unknown error'
                logger.error(f"Failed to send SMS to {to_number}: {error_message}")
                return False
        except africastalking.Service.AfricasTalkingException as e:
            logger.exception(f"Africa's Talking API error while sending SMS to {to_number}: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error while sending SMS to {to_number}: {e}")
            return False
