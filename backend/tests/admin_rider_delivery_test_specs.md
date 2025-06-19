# 🚚 Admin & Rider Delivery Workflow - Detailed Test Specifications

## 📋 Overview

This document provides comprehensive, step-by-step test case descriptions for the Admin & Rider Delivery workflow, emphasizing:

- **API interactions** (endpoints, request/response formats)
- **Expected HTTP responses** (status codes, response structures)
- **Database state changes** (specifically `Orders.order_status`, `Deliveries.delivery_status`, `Order_Items.item_status`)
- **Authentication & authorization** validation
- **Cross-system integration** testing
- **Payment processing** (Cash on Delivery handling)

---

## 🚚 Test Scenario 1: Admin Assigns Rider and Rider Completes Delivery

### **Goal**
Validate the full flow from admin assigning a delivery to a rider, to the rider updating the delivery status until completion, and the cascading status updates.

### **Pre-conditions**
- A customer has placed a confirmed order (from previous tests)
- All Order_Items for that order are packed by their respective farmers
- An admin user is authenticated
- A rider user exists, is authenticated, and has a Vehicle registered

---

### **Detailed Step-by-Step API Interactions**

#### **FULL PRE-SETUP PHASE**

**Step 1: Customer Order Creation (Reference Previous Tests)**
```python
# From previous customer shopping workflow
# Results in:
# - Order with order_id=1, order_status='confirmed'
# - Order_Items with item_status='pending'
# - Payment method (CashOnDelivery) created
```

**Step 2: Farmer Fulfillment (All Items Packed)**
```http
PATCH /api/orders/items/1/
Authorization: Bearer {farmer_jwt_token}
Content-Type: application/json

{
    "item_status": "harvested",
    "notes": "Items harvested and quality checked"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "order_item_id": 1,
    "item_status": "harvested",
    "updated_at": "2024-01-16T10:00:00Z"
}
```

**Follow-up Request:**
```http
PATCH /api/orders/items/1/
Authorization: Bearer {farmer_jwt_token}
Content-Type: application/json

{
    "item_status": "packed",
    "notes": "Items packed and ready for delivery pickup"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "order_item_id": 1,
    "item_status": "packed",
    "notes": "Items packed and ready for delivery pickup",
    "updated_at": "2024-01-16T11:00:00Z"
}
```

**Database State Change:**
- `Order_Items.item_status` = `'packed'`
- Order is now ready for delivery assignment

**Step 3: Rider and Vehicle Setup**
```http
POST /api/delivery/vehicles/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "vehicle_type": "motorcycle",
    "vehicle_model": "Honda CB150",
    "license_plate": "KAA-123B",
    "is_active": true
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "vehicle_id": 1,
    "vehicle_type": "motorcycle",
    "license_plate": "KAA-123B",
    "is_active": true,
    "rider_id": 1
}
```

---

#### **ADMIN DELIVERY ASSIGNMENT**

**Step 4: Admin Creates Delivery Assignment**
```http
POST /api/deliveries/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "order_id": 1,
    "rider_id": 1,
    "vehicle_id": 1,
    "delivery_notes": "Handle with care - organic products",
    "estimated_delivery_time": "2024-02-16T14:00:00Z"
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "delivery_id": 1,
    "order_id": 1,
    "rider_id": 1,
    "vehicle_id": 1,
    "delivery_status": "pending_pickup",
    "delivery_notes": "Handle with care - organic products",
    "estimated_delivery_time": "2024-02-16T14:00:00Z",
    "created_at": "2024-01-16T12:00:00Z",
    "assigned_by": 1  // admin user ID
}
```

**Database State Changes:**
- New `Delivery` record created with `delivery_status='pending_pickup'`
- `Orders.order_status` changes from `'confirmed'` to `'processing'`
- Delivery assignment notifications triggered

---

#### **RIDER DELIVERY WORKFLOW**

**Step 5: Rider Lists Assigned Deliveries**
```http
GET /api/deliveries/my-deliveries/
Authorization: Bearer {rider_jwt_token}
```

**Alternative Endpoints:**
- `GET /api/delivery/my-deliveries/`
- `GET /api/deliveries/` (with rider filtering)

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "delivery_id": 1,
            "order_id": 1,
            "delivery_status": "pending_pickup",
            "customer_name": "John Doe",
            "customer_phone": "0701234567",
            "delivery_address": "123 Main St, Nairobi",
            "estimated_delivery_time": "2024-02-16T14:00:00Z",
            "total_amount": "1440.00",
            "payment_method": "CashOnDelivery",
            "items_count": 1,
            "priority": "normal"
        }
    ],
    "count": 1
}
```

**Security Validation:**
- Response contains ONLY deliveries assigned to the authenticated rider
- No deliveries from other riders visible

**Step 6: Rider Retrieves Delivery Details**
```http
GET /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "order": {
        "order_id": 1,
        "total_amount": "1440.00",
        "payment_method": "CashOnDelivery",
        "special_instructions": "Please handle with care"
    },
    "customer": {
        "name": "John Doe",
        "phone": "0701234567",
        "delivery_location": {
            "address": "123 Main St, Nairobi",
            "coordinates": "1.2921,-36.8219",
            "delivery_instructions": "Gate 5, Apartment 2B"
        }
    },
    "order_items": [
        {
            "product_name": "Organic Tomatoes",
            "quantity": 8.0,
            "unit": "kg",
            "farm_name": "Green Valley Farm",
            "item_status": "packed"
        }
    ],
    "delivery_status": "pending_pickup",
    "pickup_location": {
        "farm_name": "Green Valley Farm",
        "address": "Farm Road 45, Kiambu",
        "contact_person": "Jane Farmer",
        "contact_phone": "0712345678"
    },
    "estimated_delivery_time": "2024-02-16T14:00:00Z",
    "delivery_notes": "Handle with care - organic products"
}
```

**Step 7: Rider Updates Status to 'on_the_way'**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "on_the_way",
    "pickup_time": "2024-01-16T13:00:00Z",
    "rider_notes": "Picked up from farm, heading to customer"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "on_the_way",
    "pickup_time": "2024-01-16T13:00:00Z",
    "rider_notes": "Picked up from farm, heading to customer",
    "updated_at": "2024-01-16T13:00:00Z",
    "status_history": [
        {
            "status": "pending_pickup",
            "timestamp": "2024-01-16T12:00:00Z"
        },
        {
            "status": "on_the_way",
            "timestamp": "2024-01-16T13:00:00Z",
            "notes": "Picked up from farm, heading to customer"
        }
    ]
}
```

**Database State Changes:**
- `Deliveries.delivery_status` = `'on_the_way'`
- `Deliveries.pickup_time` = `'2024-01-16T13:00:00Z'`
- `Orders.order_status` changes to `'out_for_delivery'`
- Customer notification triggered

**Step 8: Customer Verifies Order Status**
```http
GET /api/orders/1/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "order_id": 1,
    "order_status": "out_for_delivery",  // Updated by delivery status
    "delivery_info": {
        "delivery_id": 1,
        "rider_name": "Mike Rider",
        "rider_phone": "0798765432",
        "delivery_status": "on_the_way",
        "estimated_arrival": "2024-02-16T14:00:00Z"
    },
    "total_amount": "1440.00",
    "payment_status": "pending",
    "order_items": [
        {
            "product_name": "Organic Tomatoes",
            "quantity": 8.0,
            "item_status": "packed"  // Will update when delivered
        }
    ]
}
```

**Step 9: Rider Completes Delivery**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z",
    "delivery_notes": "Successfully delivered to customer",
    "customer_signature": "John Doe",
    "delivery_photo_url": "https://example.com/delivery-photo.jpg",
    "payment_collected": true,
    "payment_amount": "1440.00"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z",
    "delivery_notes": "Successfully delivered to customer",
    "customer_signature": "John Doe",
    "payment_collected": true,
    "payment_amount": "1440.00",
    "updated_at": "2024-01-16T14:15:00Z",
    "completion_confirmation": {
        "delivery_confirmed": true,
        "payment_confirmed": true,
        "customer_satisfied": true
    }
}
```

**Database State Changes (Crucial):**
- `Deliveries.delivery_status` = `'delivered'`
- `Deliveries.delivery_time` = `'2024-01-16T14:15:00Z'`
- `Orders.order_status` = `'delivered'`
- `Orders.payment_status` = `'paid'` (for CashOnDelivery)
- ALL `Order_Items.item_status` = `'delivered'`
- Transaction record created for payment

**Step 10: Customer Final Verification**
```http
GET /api/orders/1/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "order_id": 1,
    "order_status": "delivered",        // Final status
    "payment_status": "paid",           // Updated for CoD
    "delivery_info": {
        "delivery_status": "delivered",
        "delivery_time": "2024-01-16T14:15:00Z",
        "rider_name": "Mike Rider"
    },
    "order_items": [
        {
            "product_name": "Organic Tomatoes",
            "quantity": 8.0,
            "item_status": "delivered"    // Final item status
        }
    ],
    "total_amount": "1440.00",
    "order_completed_at": "2024-01-16T14:15:00Z"
}
```

---

## 🔒 Test Scenario 2: Rider Unauthorized Delivery Update

### **Goal**
Validate that a rider cannot update deliveries not assigned to them (security testing).

### **Pre-conditions**
- Two rider users (Rider A, Rider B)
- A Delivery is assigned to Rider A
- Rider B is authenticated

---

### **Detailed Step-by-Step Security Testing**

#### **SETUP PHASE**

**Step 1: Admin Creates Delivery for Rider A**
```http
POST /api/deliveries/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "order_id": 1,
    "rider_id": 1,  // Rider A
    "delivery_status": "pending_pickup"
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "delivery_id": 1,
    "rider_id": 1,
    "delivery_status": "pending_pickup"
}
```

**Step 2: Create and Authenticate Rider B**
```http
POST /api/users/register/
Content-Type: application/json

{
    "phone_number": "0799876543",
    "password": "riderb123",
    "re_password": "riderb123",
    "first_name": "Bob",
    "last_name": "RiderB",
    "user_role": "rider",
    "email": "rider.b@example.com"
}
```

**Login as Rider B:**
```http
POST /api/users/jwt/create/
Content-Type: application/json

{
    "phone_number": "0799876543",
    "password": "riderb123"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

#### **SECURITY TESTING**

**Step 3: Rider B Attempts Unauthorized Update**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_b_jwt_token}
Content-Type: application/json

{
    "delivery_status": "delivered",
    "delivery_notes": "Unauthorized delivery completion by Rider B"
}
```

**Expected Response (Security Success):**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "detail": "You do not have permission to modify this delivery",
    "error_code": "delivery_access_denied",
    "resource": "delivery",
    "resource_id": 1,
    "assigned_rider": 1,
    "requesting_rider": 2
}
```

**Alternative Expected Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Delivery not found",
    "error_code": "delivery_not_found"
}
```

**Security Analysis:**
- **403 Forbidden** = Delivery exists but rider lacks permission (explicit security)
- **404 Not Found** = Delivery not visible to rider (implicit security via filtering)
- Both responses indicate proper security implementation

**Database State Validation:**
- `Deliveries.delivery_status` remains `'pending_pickup'` (unchanged)
- `Deliveries.delivery_notes` unchanged
- No unauthorized modifications persisted

**Step 4: Rider A Verifies Delivery Integrity**
```http
GET /api/deliveries/1/
Authorization: Bearer {rider_a_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "pending_pickup",  // Original status maintained
    "delivery_notes": null,               // No unauthorized notes
    "updated_at": "2024-01-16T12:00:00Z", // Original timestamp
    "rider_id": 1                         // Still assigned to Rider A
}
```

**Step 5: Rider B List Access Security Test**
```http
GET /api/deliveries/my-deliveries/
Authorization: Bearer {rider_b_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [],  // Empty - Rider B has no assigned deliveries
    "count": 0
}
```

**Security Validation:**
- Rider B sees empty list (no access to Rider A's deliveries)
- Proper role-based access control (RBAC)
- Data isolation between riders maintained

---

## 🔄 Test Scenario 3: Valid Delivery Status Transitions

### **API Interactions for Status Transition Testing**

**Test Transition: pending_pickup → on_the_way**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "on_the_way",
    "pickup_time": "2024-01-16T13:00:00Z"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "on_the_way",
    "pickup_time": "2024-01-16T13:00:00Z",
    "updated_at": "2024-01-16T13:00:00Z"
}
```

**Test Transition: on_the_way → delivered**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z",
    "updated_at": "2024-01-16T14:15:00Z"
}
```

---

## ❌ Test Scenario 4: Invalid Delivery Status Transitions

### **API Interactions for Invalid Transition Testing**

**Invalid Transition 1: pending_pickup → delivered (skipping on_the_way)**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z"
}
```

**Expected Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Invalid delivery status transition",
    "error_code": "invalid_status_transition",
    "current_status": "pending_pickup",
    "attempted_status": "delivered",
    "valid_next_statuses": ["on_the_way"],
    "message": "Delivery must be picked up before it can be marked as delivered"
}
```

**Invalid Transition 2: delivered → on_the_way (backward)**
```http
# First complete delivery
PATCH /api/deliveries/1/
{
    "delivery_status": "on_the_way",
    "pickup_time": "2024-01-16T13:00:00Z"
}

PATCH /api/deliveries/1/
{
    "delivery_status": "delivered", 
    "delivery_time": "2024-01-16T14:15:00Z"
}

# Then try backward transition
PATCH /api/deliveries/1/
{
    "delivery_status": "on_the_way"
}
```

**Expected Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "detail": "Backward delivery status transitions are not allowed",
    "error_code": "backward_transition_denied",
    "current_status": "delivered",
    "attempted_status": "on_the_way",
    "message": "Cannot change status from delivered back to on_the_way"
}
```

---

## 💰 Test Scenario 5: Cash on Delivery Payment Integration

### **CoD Payment Processing**
```http
PATCH /api/deliveries/1/
Authorization: Bearer {rider_jwt_token}
Content-Type: application/json

{
    "delivery_status": "delivered",
    "delivery_time": "2024-01-16T14:15:00Z",
    "payment_collected": true,
    "payment_amount": "1440.00",
    "payment_method": "cash",
    "payment_notes": "Exact amount collected"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "delivery_status": "delivered",
    "payment_collected": true,
    "payment_amount": "1440.00",
    "payment_transaction": {
        "transaction_id": "TXN_001234",
        "amount": "1440.00",
        "method": "cash",
        "status": "completed",
        "timestamp": "2024-01-16T14:15:00Z"
    }
}
```

**Database State Changes:**
- `Orders.payment_status` = `'paid'`
- `Payments.Transaction` record created
- `Deliveries.payment_collected` = `true`

---

## 📊 Integration Test Endpoints

### **Admin Delivery Dashboard**
```http
GET /api/deliveries/dashboard/
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "total_deliveries": 25,
    "pending_pickup": 8,
    "on_the_way": 12,
    "delivered_today": 5,
    "pending_assignments": 3,
    "active_riders": 15,
    "average_delivery_time": "45 minutes",
    "cod_collections_today": "15750.00"
}
```

### **Rider Dashboard**
```http
GET /api/deliveries/my-deliveries/dashboard/
Authorization: Bearer {rider_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "assigned_deliveries": 5,
    "pending_pickup": 2,
    "on_the_way": 2,
    "completed_today": 1,
    "earnings_today": "2500.00",
    "next_delivery": {
        "delivery_id": 3,
        "customer_name": "Alice Johnson",
        "estimated_time": "2024-01-16T16:00:00Z"
    }
}
```

### **Customer Delivery Tracking**
```http
GET /api/deliveries/track/1/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "delivery_id": 1,
    "order_id": 1,
    "delivery_status": "on_the_way",
    "rider": {
        "name": "Mike Rider",
        "phone": "0798765432",
        "vehicle": "Honda CB150 - KAA-123B"
    },
    "estimated_arrival": "2024-01-16T14:00:00Z",
    "real_time_location": {
        "latitude": -1.2921,
        "longitude": 36.8219,
        "last_updated": "2024-01-16T13:45:00Z"
    },
    "delivery_timeline": [
        {
            "status": "pending_pickup",
            "timestamp": "2024-01-16T12:00:00Z",
            "description": "Delivery assigned to rider"
        },
        {
            "status": "on_the_way",
            "timestamp": "2024-01-16T13:00:00Z",
            "description": "Order picked up, heading to you"
        }
    ]
}
```

---

## 🎯 Key Database State Validations

### **Delivery Status Progression**
```sql
-- Initial state
SELECT delivery_status FROM deliveries WHERE delivery_id = 1;
-- Result: 'pending_pickup'

-- After pickup
SELECT delivery_status, pickup_time FROM deliveries WHERE delivery_id = 1;
-- Result: 'on_the_way', '2024-01-16 13:00:00'

-- After delivery completion
SELECT delivery_status, delivery_time, payment_collected 
FROM deliveries WHERE delivery_id = 1;
-- Result: 'delivered', '2024-01-16 14:15:00', true
```

### **Cascading Order Updates**
```sql
-- Order status synchronization
SELECT o.order_status, d.delivery_status 
FROM orders o 
JOIN deliveries d ON o.order_id = d.order_id 
WHERE o.order_id = 1;
-- Should show synchronized statuses

-- Order items final status
SELECT item_status FROM order_items 
WHERE order_id = 1;
-- All should be 'delivered' when delivery completed
```

### **Payment Integration Validation**
```sql
-- Cash on Delivery payment update
SELECT payment_status FROM orders WHERE order_id = 1;
-- Result: 'paid' (for CoD orders)

-- Transaction record creation
SELECT amount, payment_method, status 
FROM payment_transactions 
WHERE order_id = 1;
-- Should show completed cash transaction
```

---

## 🔧 Implementation Notes

### **Required Pytest Fixtures**
- `customer_client` - Authenticated customer API client
- `farmer_client` - Authenticated farmer API client
- `admin_client` - Authenticated admin API client
- `rider_client` - Authenticated rider API client
- `db_reset` - Database cleanup between tests
- `create_test_data` - Comprehensive test data setup

### **API Endpoint Patterns to Test**
- `/api/deliveries/` (admin delivery management)
- `/api/deliveries/my-deliveries/` (rider-specific deliveries)
- `/api/deliveries/{id}/` (specific delivery details/updates)
- `/api/delivery/vehicles/` (vehicle management)
- `/api/deliveries/track/{id}/` (customer tracking)

### **Error Handling Validations**
- **401 Unauthorized** - Missing/invalid JWT token
- **403 Forbidden** - Valid token, insufficient permissions
- **404 Not Found** - Delivery doesn't exist or not accessible
- **400 Bad Request** - Invalid status transitions, validation errors

### **Status Transition Rules**
- **Valid Flow:** `pending_pickup` → `on_the_way` → `delivered`
- **Invalid:** Skipping statuses or backward transitions
- **Required Fields:** `pickup_time` for `on_the_way`, `delivery_time` for `delivered`

### **Payment Processing Rules**
- **Cash on Delivery:** Payment status updates only when delivery completed
- **Payment Collection:** Rider must confirm payment received
- **Transaction Records:** Automatic creation for successful payments

This comprehensive test specification ensures thorough validation of the Admin & Rider Delivery workflow with detailed API interactions, security testing, payment processing, and cascading status management across the entire marketplace system. 