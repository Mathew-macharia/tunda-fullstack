import requests
import base64
import json
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from core.models import SystemSettings

logger = logging.getLogger(__name__)

class MpesaService:
    """
    Service class for handling M-Pesa API interactions
    Integrates with Safaricom's Daraja API for STK Push payments
    """
    
    def __init__(self):
        """Initialize M-Pesa service with settings from database"""
        self.consumer_key = SystemSettings.objects.get_setting('mpesa_consumer_key', '')
        self.consumer_secret = SystemSettings.objects.get_setting('mpesa_consumer_secret', '')
        self.business_shortcode = SystemSettings.objects.get_setting('mpesa_business_shortcode', '')
        self.passkey = SystemSettings.objects.get_setting('mpesa_passkey', '')
        self.environment = SystemSettings.objects.get_setting('mpesa_environment', 'sandbox')
        self.callback_url = SystemSettings.objects.get_setting('mpesa_callback_url', '')
        
        # Set API URLs based on environment
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required M-Pesa settings are configured"""
        required_settings = [
            ('consumer_key', self.consumer_key),
            ('consumer_secret', self.consumer_secret),
            ('business_shortcode', self.business_shortcode),
            ('passkey', self.passkey),
            ('callback_url', self.callback_url)
        ]
        
        missing_settings = [name for name, value in required_settings if not value]
        
        if missing_settings:
            raise ValueError(
                f"Missing required M-Pesa settings: {', '.join(missing_settings)}. "
                "Please configure these in the system settings."
            )
    
    def get_access_token(self):
        """
        Get M-Pesa API access token using consumer key and secret
        
        Returns:
            str: Access token for API authentication
            
        Raises:
            Exception: If authentication fails
        """
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create base64 encoded credentials
            credentials = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Requesting M-Pesa access token from {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            access_token = data.get('access_token')
            
            if not access_token:
                raise Exception("No access token received from M-Pesa API")
            
            logger.info("Successfully obtained M-Pesa access token")
            return access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting M-Pesa access token: {str(e)}")
            raise Exception(f"Failed to connect to M-Pesa API: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting M-Pesa access token: {str(e)}")
            raise Exception(f"M-Pesa authentication failed: {str(e)}")
    
    def _generate_password(self, timestamp):
        """
        Generate password for STK Push request
        
        Args:
            timestamp (str): Timestamp in format YYYYMMDDHHMMSS
            
        Returns:
            str: Base64 encoded password
        """
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password
    
    def _format_phone_number(self, phone_number):
        """
        Format phone number to the required format (254XXXXXXXXX)
        
        Args:
            phone_number (str): Phone number in various formats
            
        Returns:
            str: Formatted phone number
        """
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different formats
        if phone.startswith('254'):
            return phone
        elif phone.startswith('0'):
            return '254' + phone[1:]
        elif len(phone) == 9:
            return '254' + phone
        else:
            raise ValueError(f"Invalid phone number format: {phone_number}")
    
    def initiate_stk_push(self, phone_number, amount, reference, description=None, reference_type='order'):
        """
        Initiate M-Pesa STK Push payment request
        Supports both session-based and order-based payments
        
        Args:
            phone_number (str): Customer phone number
            amount (Decimal): Payment amount
            reference (str): Payment reference (session ID or order ID)
            description (str, optional): Transaction description
            reference_type (str): Type of reference ('session' or 'order')
            
        Returns:
            dict: M-Pesa API response
            
        Raises:
            Exception: If STK Push initiation fails
        """
        try:
            access_token = self.get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            # Format phone number
            formatted_phone = self._format_phone_number(phone_number)
            
            # Prepare reference and description based on type
            if reference_type == 'session':
                account_reference = f'Session-{reference}'
                default_description = f'Payment for session {reference}'
            else:
                account_reference = f'Order-{reference}'
                default_description = f'Payment for order {reference}'
            
            # Prepare API request
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(float(amount)),  # Convert to integer
                'PartyA': formatted_phone,
                'PartyB': self.business_shortcode,
                'PhoneNumber': formatted_phone,
                'CallBackURL': self.callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': description or default_description
            }
            
            logger.info(f"Initiating STK Push for phone {formatted_phone}, amount {amount}, reference {reference} ({reference_type})")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Log the response for debugging
            logger.info(f"STK Push response: {json.dumps(data, indent=2)}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error initiating STK Push: {str(e)}")
            raise Exception(f"Failed to connect to M-Pesa API: {str(e)}")
        except Exception as e:
            logger.error(f"Error initiating STK Push: {str(e)}")
            raise Exception(f"STK Push initiation failed: {str(e)}")
    
    def query_transaction_status(self, checkout_request_id):
        """
        Query the status of a transaction using checkout request ID
        
        Args:
            checkout_request_id (str): Checkout request ID from STK Push
            
        Returns:
            dict: Transaction status response
            
        Raises:
            Exception: If status query fails
        """
        try:
            access_token = self.get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }
            
            logger.info(f"Querying transaction status for checkout request: {checkout_request_id}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Transaction status response: {json.dumps(data, indent=2)}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error querying transaction status: {str(e)}")
            raise Exception(f"Failed to connect to M-Pesa API: {str(e)}")
        except Exception as e:
            logger.error(f"Error querying transaction status: {str(e)}")
            raise Exception(f"Transaction status query failed: {str(e)}")
    
    def process_callback(self, callback_data):
        """
        Process M-Pesa callback data and extract relevant information
        
        Args:
            callback_data (dict): Raw callback data from M-Pesa
            
        Returns:
            dict: Processed callback information
        """
        try:
            # Extract STK callback data
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            result = {
                'checkout_request_id': stk_callback.get('CheckoutRequestID'),
                'merchant_request_id': stk_callback.get('MerchantRequestID'),
                'result_code': stk_callback.get('ResultCode'),
                'result_desc': stk_callback.get('ResultDesc'),
                'amount': None,
                'mpesa_receipt_number': None,
                'transaction_date': None,
                'phone_number': None
            }
            
            # If successful, extract additional details from callback metadata
            if result['result_code'] == 0:
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                
                for item in callback_metadata:
                    name = item.get('Name')
                    value = item.get('Value')
                    
                    if name == 'Amount':
                        result['amount'] = value
                    elif name == 'MpesaReceiptNumber':
                        result['mpesa_receipt_number'] = value
                    elif name == 'TransactionDate':
                        result['transaction_date'] = value
                    elif name == 'PhoneNumber':
                        result['phone_number'] = value
            
            logger.info(f"Processed callback data: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {str(e)}")
            raise Exception(f"Callback processing failed: {str(e)}")
    
    def validate_callback_signature(self, callback_data, signature=None):
        """
        Validate M-Pesa callback signature (if available)
        
        Args:
            callback_data (dict): Callback data
            signature (str, optional): Callback signature
            
        Returns:
            bool: True if signature is valid or validation is skipped
        """
        # Note: M-Pesa doesn't always provide signatures in callbacks
        # This method is here for future enhancement if needed
        # For now, we'll rely on the callback URL being secure (HTTPS)
        # and potentially IP whitelisting
        
        return True
    
    def get_environment_info(self):
        """
        Get current M-Pesa environment configuration info
        
        Returns:
            dict: Environment configuration details
        """
        return {
            'environment': self.environment,
            'base_url': self.base_url,
            'business_shortcode': self.business_shortcode,
            'callback_url': self.callback_url,
            'has_credentials': bool(self.consumer_key and self.consumer_secret)
        } 