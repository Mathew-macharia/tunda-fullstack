# M-Pesa Integration Guide

This guide explains how to set up and use the M-Pesa payment integration in the Vegas Inc platform.

## Overview

The M-Pesa integration provides:
- **STK Push** payments for seamless customer checkout
- **Real-time payment verification** via callbacks
- **Payment status tracking** and management
- **Production-ready** implementation with proper error handling

## Prerequisites

### 1. M-Pesa Developer Account
You need a Safaricom M-Pesa Developer account:
1. Visit [https://developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an account and verify your email
3. Create a new app in the Daraja Portal

### 2. Required Credentials
From your Daraja Portal app, you'll need:
- **Consumer Key** - Your app's consumer key
- **Consumer Secret** - Your app's consumer secret
- **Business Shortcode** - Your business shortcode (Till/PayBill number)
- **Passkey** - STK Push passkey for your shortcode
- **Environment** - `sandbox` for testing, `production` for live

## Setup Instructions

### Step 1: Install Dependencies
The M-Pesa integration requires the `requests` library (already added to requirements.txt):
```bash
pip install requests==2.31.0
```

### Step 2: Run Database Migrations
```bash
python manage.py migrate
```

### Step 3: Initialize M-Pesa Settings
```bash
python manage.py init_mpesa_settings
```

### Step 4: Configure M-Pesa Credentials

#### Option A: Interactive Setup (Recommended)
```bash
python manage.py set_mpesa_credentials --interactive
```

#### Option B: Command Line Arguments
```bash
python manage.py set_mpesa_credentials \
    --consumer-key "YOUR_CONSUMER_KEY" \
    --consumer-secret "YOUR_CONSUMER_SECRET" \
    --business-shortcode "YOUR_SHORTCODE" \
    --passkey "YOUR_PASSKEY" \
    --environment "sandbox" \
    --callback-url "https://yourdomain.com/api/payments/transactions/mpesa_callback/"
```

#### Option C: Admin Panel
1. Go to Django Admin → Core → System Settings
2. Find and update the M-Pesa settings:
   - `mpesa_consumer_key`
   - `mpesa_consumer_secret`
   - `mpesa_business_shortcode`
   - `mpesa_passkey`
   - `mpesa_environment`
   - `mpesa_callback_url`

### Step 5: Configure Callback URL
Set your callback URL to: `https://yourdomain.com/api/payments/transactions/mpesa_callback/`

**Important**: The callback URL must be HTTPS in production.

## API Endpoints

### 1. Initiate M-Pesa Payment
```http
POST /api/payments/transactions/initiate_mpesa_payment/
Content-Type: application/json
Authorization: JWT <token>

{
    "order_id": 123,
    "phone_number": "254712345678"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "STK Push sent successfully. Please check your phone.",
    "transaction_id": 456,
    "checkout_request_id": "ws_CO_123456789",
    "customer_message": "Please check your phone for M-Pesa prompt."
}
```

### 2. Check Payment Status
```http
GET /api/payments/transactions/456/check_mpesa_status/
Authorization: JWT <token>
```

**Response:**
```json
{
    "transaction": {
        "transaction_id": 456,
        "payment_status": "completed",
        "mpesa_receipt_number": "NLJ7RT61SV",
        "amount": "1500.00",
        "phone_number": "254712345678"
    },
    "mpesa_status": {
        "ResultCode": "0",
        "ResultDesc": "The service request is processed successfully."
    }
}
```

### 3. M-Pesa Callback (Webhook)
```http
POST /api/payments/transactions/mpesa_callback/
Content-Type: application/json

{
    "Body": {
        "stkCallback": {
            "CheckoutRequestID": "ws_CO_123456789",
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "CallbackMetadata": {
                "Item": [
                    {"Name": "Amount", "Value": 1500},
                    {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                    {"Name": "TransactionDate", "Value": 20230101120000},
                    {"Name": "PhoneNumber", "Value": 254712345678}
                ]
            }
        }
    }
}
```

## Frontend Integration

The frontend checkout page automatically handles M-Pesa payments:

1. **Order Creation**: Creates order with pending payment status
2. **STK Push**: Initiates M-Pesa payment request
3. **Payment Modal**: Shows real-time payment status
4. **Status Polling**: Checks payment status every 10 seconds
5. **Completion**: Redirects to order details on success

### Key Features:
- **Real-time feedback** with animated payment modal
- **Retry functionality** for failed payments
- **Timeout handling** with manual verification option
- **Receipt display** with M-Pesa receipt number

## Testing

### Sandbox Testing
1. Set environment to `sandbox`
2. Use Safaricom's test credentials
3. Test phone numbers: `254708374149`, `254711222333`

### Test Scenarios:
- **Successful payment**: Complete STK Push flow
- **Failed payment**: Cancel or timeout STK Push
- **Network issues**: Test callback handling
- **Invalid phone**: Test validation

## Production Deployment

### 1. Environment Configuration
```bash
python manage.py set_mpesa_credentials \
    --environment "production" \
    --callback-url "https://yourdomain.com/api/payments/transactions/mpesa_callback/"
```

### 2. SSL Certificate
Ensure your callback URL uses HTTPS with a valid SSL certificate.

### 3. Callback URL Registration
Register your callback URL in the Safaricom Daraja Portal.

### 4. IP Whitelisting (Optional)
Consider whitelisting Safaricom's IP ranges for enhanced security.

## Monitoring and Logging

### Payment Transaction Logs
All payment transactions are logged with:
- Transaction IDs and status
- M-Pesa receipt numbers
- Error messages and retry attempts
- Callback data for debugging

### System Logs
Check Django logs for:
```python
logger = logging.getLogger('payments.mpesa')
```

## Troubleshooting

### Common Issues:

1. **"Missing required M-Pesa settings"**
   - Run `python manage.py init_mpesa_settings` to check configuration
   - Ensure all credentials are set correctly

2. **"Failed to connect to M-Pesa API"**
   - Check internet connectivity
   - Verify API endpoints (sandbox vs production)
   - Check if credentials are valid

3. **"Callback not received"**
   - Verify callback URL is accessible via HTTPS
   - Check if URL is registered in Daraja Portal
   - Ensure callback endpoint is not blocked by firewall

4. **"Invalid phone number format"**
   - Phone numbers must be in format: `254XXXXXXXXX`
   - Remove any spaces or special characters

### Debug Commands:
```bash
# Check M-Pesa settings
python manage.py init_mpesa_settings

# Test M-Pesa connectivity (create custom command)
python manage.py test_mpesa_connection

# View recent transactions
python manage.py shell
>>> from payments.models import PaymentTransaction
>>> PaymentTransaction.objects.filter(payment_method__payment_type='Mpesa').order_by('-created_at')[:5]
```

## Security Considerations

1. **Credentials Security**: Store M-Pesa credentials securely (environment variables recommended)
2. **Callback Validation**: Validate callback signatures if available
3. **Rate Limiting**: Implement rate limiting on payment endpoints
4. **Logging**: Log all payment attempts for audit trails
5. **HTTPS**: Always use HTTPS for callback URLs in production

## Support

For M-Pesa API issues:
- Safaricom Developer Support: [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
- M-Pesa API Documentation: Available in Daraja Portal

For implementation issues:
- Check Django logs for detailed error messages
- Use the debug commands provided above
- Review the payment transaction records in the admin panel 