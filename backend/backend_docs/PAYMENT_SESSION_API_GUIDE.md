# 🚀 Payment Session API Guide

## Overview

The Payment Session API implements a **payment-first approach** where customers complete payment before order creation. This ensures:

- ✅ **No inventory issues** (stock only reduced after payment)
- ✅ **Clean payment flow** (no orphaned orders)
- ✅ **Better error handling** (failed payments don't create problematic orders)
- ✅ **Complete audit trail** (every payment attempt is tracked)

## 🔄 Payment Flow

```
1. Customer adds items to cart
2. Customer proceeds to checkout
3. CREATE PaymentSession (cart snapshot created)
4. INITIATE M-Pesa payment for session
5. Customer completes M-Pesa payment
6. M-Pesa callback triggers order creation
7. Customer redirected to order tracking
```

## 📋 API Endpoints

### 1. Create Payment Session

**Endpoint:** `POST /api/payments/sessions/`

**Description:** Creates a payment session from the user's current cart

**Request Body:**
```json
{
  "delivery_details": {
    "full_name": "John Doe",
    "phone_number": "0712345678",
    "county_id": 1,
    "subcounty_id": 5,
    "detailed_address": "123 Main Street, Apartment 4B"
  },
  "special_instructions": "Leave at the gate",
  "delivery_time_slot": "morning",
  "estimated_delivery_date": "2024-01-15"
}
```

**Response (201 Created):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user": 1,
  "cart_snapshot": {
    "items": [
      {
        "cart_item_id": 1,
        "listing_id": 123,
        "product_name": "Fresh Tomatoes",
        "farm_name": "Green Valley Farm",
        "quantity": 2.0,
        "price_at_addition": 150.00,
        "subtotal": 300.00,
        "unit_of_measure": "kg"
      }
    ],
    "total_items": 2,
    "total_cost": 300.00,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "delivery_details": {
    "full_name": "John Doe",
    "phone_number": "0712345678",
    "county_id": 1,
    "subcounty_id": 5,
    "detailed_address": "123 Main Street, Apartment 4B",
    "special_instructions": "Leave at the gate",
    "delivery_time_slot": "morning",
    "estimated_delivery_date": "2024-01-15"
  },
  "total_amount": "350.00",
  "delivery_fee": "50.00",
  "phone_number": "0712345678",
  "session_status": "pending",
  "order": null,
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T10:45:00Z"
}
```

### 2. Initiate Payment for Session

**Endpoint:** `POST /api/payments/sessions/{session_id}/initiate_payment/`

**Description:** Initiates M-Pesa STK Push payment for a payment session

**Request Body:**
```json
{
  "phone_number": "0712345678"  // Optional: override session phone
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "STK Push sent successfully. Please check your phone.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "transaction_id": 456,
  "checkout_request_id": "ws_CO_15012024103045123",
  "customer_message": "Please check your phone for M-Pesa prompt."
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Session has expired",
  "error_code": "SESSION_EXPIRED"
}
```

### 3. Check Session Status

**Endpoint:** `GET /api/payments/sessions/{session_id}/status/`

**Description:** Check the current status of a payment session

**Response (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_status": "paid",
  "order": {
    "order_id": 789,
    "order_number": "ORD-20240115-001",
    "order_status": "confirmed",
    "payment_status": "paid"
  },
  "expires_at": "2024-01-15T10:45:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Extend Session

**Endpoint:** `POST /api/payments/sessions/{session_id}/extend_session/`

**Description:** Extend the expiry time of a payment session

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Session extended",
  "expires_at": "2024-01-15T11:00:00Z"
}
```

### 5. List User Sessions

**Endpoint:** `GET /api/payments/sessions/`

**Description:** List all payment sessions for the authenticated user

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "session_status": "order_created",
      "total_amount": "350.00",
      "created_at": "2024-01-15T10:30:00Z",
      "order_details": {
        "order_id": 789,
        "order_number": "ORD-20240115-001"
      }
    }
  ]
}
```

## 🔄 Session Status Flow

```
pending → payment_initiated → paid → order_created
    ↓           ↓              ↓
  expired     failed        failed
```

**Status Descriptions:**
- `pending`: Session created, awaiting payment initiation
- `payment_initiated`: M-Pesa STK Push sent, awaiting user response
- `paid`: Payment completed successfully
- `failed`: Payment failed or was cancelled
- `expired`: Session expired (15 minutes default)
- `order_created`: Order successfully created from paid session

## 🔧 M-Pesa Callback Integration

The M-Pesa callback automatically handles session-based payments:

**Callback URL:** `POST /api/payments/transactions/mpesa_callback/`

**Callback Flow:**
1. M-Pesa sends callback with payment result
2. System finds PaymentTransaction by `checkout_request_id`
3. If payment successful:
   - Session status → `paid`
   - Order created from session
   - Transaction linked to order
   - Session status → `order_created`
4. If payment failed:
   - Session status → `failed`

## 📱 Frontend Integration

### JavaScript Example

```javascript
// 1. Create payment session
const createSession = async (deliveryDetails) => {
  const response = await fetch('/api/payments/sessions/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      delivery_details: deliveryDetails,
      special_instructions: "Handle with care"
    })
  });
  return response.json();
};

// 2. Initiate payment
const initiatePayment = async (sessionId, phoneNumber) => {
  const response = await fetch(`/api/payments/sessions/${sessionId}/initiate_payment/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ phone_number: phoneNumber })
  });
  return response.json();
};

// 3. Poll session status
const pollSessionStatus = async (sessionId) => {
  const response = await fetch(`/api/payments/sessions/${sessionId}/status/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  if (data.session_status === 'order_created') {
    // Redirect to order tracking
    window.location.href = `/orders/${data.order.order_id}`;
  } else if (data.session_status === 'failed') {
    // Show error message
    alert('Payment failed. Please try again.');
  }
  
  return data;
};

// Complete checkout flow
const checkout = async (deliveryDetails, phoneNumber) => {
  try {
    // 1. Create session
    const session = await createSession(deliveryDetails);
    
    // 2. Initiate payment
    const payment = await initiatePayment(session.session_id, phoneNumber);
    
    if (payment.status === 'success') {
      // 3. Poll for status updates
      const interval = setInterval(async () => {
        const status = await pollSessionStatus(session.session_id);
        
        if (status.session_status === 'order_created') {
          clearInterval(interval);
          // Redirect to success page
        } else if (status.session_status === 'failed') {
          clearInterval(interval);
          // Show error
        }
      }, 3000); // Poll every 3 seconds
      
      // Stop polling after 5 minutes
      setTimeout(() => clearInterval(interval), 300000);
    }
  } catch (error) {
    console.error('Checkout failed:', error);
  }
};
```

## 🔒 Security & Validation

### Authentication
- All endpoints require authentication
- Users can only access their own sessions

### Validation
- Cart must not be empty when creating session
- Session must not be expired for payment initiation
- Phone number format validation
- County/subcounty existence validation

### Error Handling
- Comprehensive error messages
- Proper HTTP status codes
- Transaction rollback on failures

## 📊 Monitoring & Analytics

### Key Metrics to Track
- Session creation rate
- Payment initiation rate
- Payment success rate
- Session expiry rate
- Order creation success rate

### Database Queries
```sql
-- Sessions by status
SELECT session_status, COUNT(*) 
FROM Payment_Sessions 
GROUP BY session_status;

-- Success rate
SELECT 
  COUNT(CASE WHEN session_status = 'order_created' THEN 1 END) * 100.0 / COUNT(*) as success_rate
FROM Payment_Sessions 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR);
```

## 🚀 Production Deployment

### Environment Variables
```env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/transactions/mpesa_callback/
MPESA_ENVIRONMENT=production
```

### M-Pesa Settings Setup
```bash
python manage.py set_mpesa_credentials
```

This implementation provides a robust, production-ready M-Pesa integration with the payment-first approach! 