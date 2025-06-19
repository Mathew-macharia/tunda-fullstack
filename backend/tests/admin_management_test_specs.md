# 🔧 Admin & Core Management Workflow - Detailed Test Specifications

## 📋 Overview

This document provides comprehensive, step-by-step test case descriptions for the Admin & Core Management workflows, emphasizing:

- **API interactions** (endpoints, request/response formats)
- **Expected HTTP responses** (status codes, response structures)
- **Database state changes** (system settings, market data, support tickets, reviews, payouts)
- **Authentication & authorization** validation
- **Content moderation** and business operations
- **Financial management** and audit trails

---

## 🔧 Test Scenario 1: Admin Manages System Settings Successfully

### **Goal**
Validate an admin can create, read, update, and delete system settings while ensuring proper access control.

### **Pre-conditions**
- Authenticated admin user
- Non-admin users for security testing

---

### **Detailed Step-by-Step API Interactions**

#### **ADMIN SYSTEM SETTINGS MANAGEMENT**

**Step 1: Admin Creates New System Setting**
```http
POST /api/core/settings/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "setting_key": "tax_rate",
    "setting_value": "0.16",
    "setting_type": "number",
    "description": "Default tax rate for transactions",
    "is_active": true
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "setting_id": 1,
    "setting_key": "tax_rate",
    "setting_value": "0.16",
    "setting_type": "number",
    "description": "Default tax rate for transactions",
    "is_active": true,
    "created_by": 1,
    "created_at": "2024-01-16T10:00:00Z",
    "updated_at": "2024-01-16T10:00:00Z"
}
```

**Database State Change:**
- `System_Settings.setting_key` = `'tax_rate'`
- `System_Settings.setting_value` = `'0.16'`
- `System_Settings.created_by` = admin user ID

**Step 2: Admin Retrieves System Setting by Key**
```http
GET /api/core/settings/tax_rate/
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "setting_id": 1,
    "setting_key": "tax_rate",
    "setting_value": "0.16",
    "setting_type": "number",
    "description": "Default tax rate for transactions",
    "is_active": true,
    "last_modified_by": 1,
    "version": 1
}
```

**Step 3: Admin Updates System Setting**
```http
PATCH /api/core/settings/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "setting_value": "0.18",
    "description": "Updated tax rate for 2024"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "setting_id": 1,
    "setting_key": "tax_rate",
    "setting_value": "0.18",
    "setting_type": "number",
    "description": "Updated tax rate for 2024",
    "is_active": true,
    "updated_at": "2024-01-16T11:00:00Z",
    "last_modified_by": 1,
    "version": 2
}
```

**Database State Change:**
- `System_Settings.setting_value` = `'0.18'`
- `System_Settings.version` incremented
- Audit log entry created

**Step 4: Admin Lists All System Settings**
```http
GET /api/core/settings/
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "setting_id": 1,
            "setting_key": "tax_rate",
            "setting_value": "0.18",
            "setting_type": "number",
            "description": "Updated tax rate for 2024",
            "is_active": true
        },
        {
            "setting_id": 2,
            "setting_key": "max_delivery_distance",
            "setting_value": "50",
            "setting_type": "number",
            "description": "Maximum delivery distance in kilometers"
        }
    ],
    "count": 2
}
```

**Step 5: Admin Deletes System Setting**
```http
DELETE /api/core/settings/1/
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 204 No Content
```

**Database State Change:**
- `System_Settings` record deleted or marked inactive
- Audit log entry for deletion

#### **SECURITY TESTING**

**Step 6: Customer Attempts Unauthorized Setting Creation**
```http
POST /api/core/settings/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "setting_key": "unauthorized_setting",
    "setting_value": "malicious_value",
    "setting_type": "string"
}
```

**Expected Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "detail": "You do not have permission to manage system settings",
    "error_code": "insufficient_permissions",
    "required_role": "admin"
}
```

**Step 7: Customer Attempts to List System Settings**
```http
GET /api/core/settings/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "detail": "Administrative access required",
    "error_code": "admin_access_required"
}
```

---

## 📈 Test Scenario 2: Admin Manages Market Prices & Weather Alerts

### **Goal**
Validate admin can manage market data and weather alerts, with appropriate user access for viewing.

### **Pre-conditions**
- Authenticated admin user
- Existing Product and Location records
- Authenticated farmer and customer users

---

### **Detailed Step-by-Step API Interactions**

#### **MARKET PRICE MANAGEMENT**

**Step 1: Admin Creates Market Price Record**
```http
POST /api/data_insights/market-prices/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "product_id": 1,
    "location_id": 1,
    "price_date": "2024-01-16",
    "average_price": 250.00,
    "min_price": 200.00,
    "max_price": 300.00,
    "price_unit": "per_kg",
    "market_source": "Nairobi Central Market",
    "data_quality": "verified",
    "sample_size": 25
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "price_id": 1,
    "product": {
        "product_id": 1,
        "product_name": "Tomatoes",
        "category": "Vegetables"
    },
    "location": {
        "location_id": 1,
        "location_name": "Nairobi",
        "county": "Nairobi"
    },
    "price_date": "2024-01-16",
    "average_price": "250.00",
    "min_price": "200.00",
    "max_price": "300.00",
    "price_unit": "per_kg",
    "market_source": "Nairobi Central Market",
    "created_at": "2024-01-16T12:00:00Z",
    "created_by": 1
}
```

**Database State Change:**
- New `Market_Price` record created
- Price history maintained
- Data quality flags set

**Step 2: Admin Updates Market Price**
```http
PATCH /api/data_insights/market-prices/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "average_price": 275.00,
    "max_price": 320.00,
    "notes": "Price increase due to seasonal demand",
    "data_quality": "verified"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "price_id": 1,
    "average_price": "275.00",
    "max_price": "320.00",
    "notes": "Price increase due to seasonal demand",
    "updated_at": "2024-01-16T13:00:00Z",
    "last_modified_by": 1
}
```

#### **WEATHER ALERT MANAGEMENT**

**Step 3: Admin Creates Weather Alert**
```http
POST /api/communication/weather-alerts/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "location_id": 1,
    "alert_type": "heavy_rain",
    "severity": "high",
    "title": "Heavy Rain Warning",
    "message": "Heavy rains expected in the next 24 hours. Farmers advised to protect crops.",
    "valid_from": "2024-01-16T14:00:00Z",
    "valid_until": "2024-01-17T23:59:59Z",
    "is_active": true,
    "source": "Kenya Meteorological Department"
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "alert_id": 1,
    "location": {
        "location_id": 1,
        "location_name": "Nairobi"
    },
    "alert_type": "heavy_rain",
    "severity": "high",
    "title": "Heavy Rain Warning",
    "message": "Heavy rains expected in the next 24 hours. Farmers advised to protect crops.",
    "valid_from": "2024-01-16T14:00:00Z",
    "valid_until": "2024-01-17T23:59:59Z",
    "is_active": true,
    "created_at": "2024-01-16T12:30:00Z",
    "created_by": 1
}
```

**Database State Change:**
- New `Weather_Alert` record created
- Alert status tracking initiated
- Notification queue populated

#### **USER ACCESS VALIDATION**

**Step 4: Farmer Views Weather Alerts**
```http
GET /api/communication/weather-alerts/?location_id=1
Authorization: Bearer {farmer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "alert_id": 1,
            "alert_type": "heavy_rain",
            "severity": "high",
            "title": "Heavy Rain Warning",
            "message": "Heavy rains expected in the next 24 hours. Farmers advised to protect crops.",
            "valid_from": "2024-01-16T14:00:00Z",
            "valid_until": "2024-01-17T23:59:59Z",
            "is_active": true
        }
    ],
    "count": 1
}
```

**Step 5: Customer Views Market Prices**
```http
GET /api/data_insights/market-prices/?product_id=1&location_id=1
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "price_id": 1,
            "product_name": "Tomatoes",
            "location_name": "Nairobi",
            "price_date": "2024-01-16",
            "average_price": "275.00",
            "min_price": "200.00",
            "max_price": "320.00",
            "price_unit": "per_kg",
            "trend": "increasing"
        }
    ],
    "count": 1
}
```

---

## 🎫 Test Scenario 3: User Creates and Admin Manages Support Tickets

### **Goal**
Validate complete support ticket lifecycle from user creation to admin resolution.

### **Pre-conditions**
- Authenticated customer and admin users
- Support ticket categories configured

---

### **Detailed Step-by-Step API Interactions**

#### **CUSTOMER SUPPORT TICKET CREATION**

**Step 1: Customer Creates Support Ticket**
```http
POST /api/communication/support-tickets/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "subject": "Issue with Order Delivery",
    "message": "My order was not delivered on time and I need assistance.",
    "category": "delivery",
    "priority": "medium",
    "order_id": 1,
    "contact_method": "email"
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "ticket_id": 1,
    "ticket_number": "TKT-20240116-001",
    "subject": "Issue with Order Delivery",
    "message": "My order was not delivered on time and I need assistance.",
    "category": "delivery",
    "priority": "medium",
    "status": "open",
    "created_by": 2,
    "created_at": "2024-01-16T09:00:00Z",
    "estimated_response_time": "2024-01-16T17:00:00Z"
}
```

**Database State Change:**
- New `Support_Ticket` record created
- Ticket number auto-generated
- Initial status set to 'open'
- SLA timer started

**Step 2: Customer Lists Own Support Tickets**
```http
GET /api/communication/support-tickets/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "ticket_id": 1,
            "ticket_number": "TKT-20240116-001",
            "subject": "Issue with Order Delivery",
            "status": "open",
            "priority": "medium",
            "created_at": "2024-01-16T09:00:00Z",
            "last_updated": "2024-01-16T09:00:00Z"
        }
    ],
    "count": 1
}
```

#### **ADMIN TICKET MANAGEMENT**

**Step 3: Admin Lists All Support Tickets**
```http
GET /api/communication/support-tickets/?status=all
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "ticket_id": 1,
            "ticket_number": "TKT-20240116-001",
            "subject": "Issue with Order Delivery",
            "customer": {
                "user_id": 2,
                "name": "John Doe",
                "email": "john@example.com"
            },
            "category": "delivery",
            "priority": "medium",
            "status": "open",
            "created_at": "2024-01-16T09:00:00Z",
            "sla_status": "within_sla"
        }
    ],
    "count": 1,
    "summary": {
        "open": 1,
        "in_progress": 0,
        "resolved": 0,
        "overdue": 0
    }
}
```

**Step 4: Admin Retrieves Specific Ticket Details**
```http
GET /api/communication/support-tickets/1/
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "ticket_id": 1,
    "ticket_number": "TKT-20240116-001",
    "subject": "Issue with Order Delivery",
    "message": "My order was not delivered on time and I need assistance.",
    "category": "delivery",
    "priority": "medium",
    "status": "open",
    "customer": {
        "user_id": 2,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "0701234567"
    },
    "related_order": {
        "order_id": 1,
        "order_date": "2024-01-15T10:00:00Z",
        "delivery_status": "delayed"
    },
    "created_at": "2024-01-16T09:00:00Z",
    "sla_deadline": "2024-01-16T17:00:00Z"
}
```

**Step 5: Admin Updates Ticket to In Progress**
```http
PATCH /api/communication/support-tickets/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "status": "in_progress",
    "assigned_to": 1,
    "admin_notes": "Investigating delivery issue with logistics team",
    "internal_priority": "high"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "ticket_id": 1,
    "status": "in_progress",
    "assigned_to": {
        "user_id": 1,
        "name": "Admin User"
    },
    "admin_notes": "Investigating delivery issue with logistics team",
    "updated_at": "2024-01-16T10:00:00Z",
    "status_history": [
        {
            "status": "open",
            "timestamp": "2024-01-16T09:00:00Z"
        },
        {
            "status": "in_progress", 
            "timestamp": "2024-01-16T10:00:00Z",
            "changed_by": 1
        }
    ]
}
```

**Database State Change:**
- `Support_Ticket.status` = `'in_progress'`
- `Support_Ticket.assigned_to` = admin user ID
- Status history entry added
- Customer notification triggered

**Step 6: Admin Resolves Ticket**
```http
PATCH /api/communication/support-tickets/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "status": "resolved",
    "resolution_notes": "Issue resolved. Delivery was delayed due to weather. Customer compensated with 10% discount on next order.",
    "resolved_at": "2024-01-16T15:30:00Z",
    "resolution_time_minutes": 390,
    "customer_satisfaction_survey_sent": true
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "ticket_id": 1,
    "status": "resolved",
    "resolution_notes": "Issue resolved. Delivery was delayed due to weather. Customer compensated with 10% discount on next order.",
    "resolved_at": "2024-01-16T15:30:00Z",
    "resolution_time_minutes": 390,
    "sla_met": true,
    "updated_at": "2024-01-16T15:30:00Z"
}
```

**Database State Change:**
- `Support_Ticket.status` = `'resolved'`
- `Support_Ticket.resolved_at` timestamp set
- SLA compliance calculated
- Customer satisfaction survey triggered

#### **CUSTOMER VERIFICATION**

**Step 7: Customer Views Resolved Ticket**
```http
GET /api/communication/support-tickets/1/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "ticket_id": 1,
    "ticket_number": "TKT-20240116-001",
    "subject": "Issue with Order Delivery",
    "status": "resolved",
    "resolution_notes": "Issue resolved. Delivery was delayed due to weather. Customer compensated with 10% discount on next order.",
    "resolved_at": "2024-01-16T15:30:00Z",
    "can_reopen": true,
    "satisfaction_survey_url": "https://tunda-soko.com/survey/1"
}
```

#### **SECURITY TESTING**

**Step 8: Customer Attempts Unauthorized Ticket Access**
```http
PATCH /api/communication/support-tickets/2/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "status": "resolved",
    "message": "Unauthorized attempt to resolve ticket"
}
```

**Expected Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "detail": "You can only modify your own support tickets",
    "error_code": "ticket_access_denied",
    "ticket_owner": 3,
    "requesting_user": 2
}
```

---

## ⭐ Test Scenario 4: User Creates Review, Admin Moderates

### **Goal**
Validate complete review lifecycle with user creation and admin moderation capabilities.

### **Pre-conditions**
- Customer with completed order (delivered status)
- Authenticated admin user
- Product, farmer, and rider available for review

---

### **Detailed Step-by-Step API Interactions**

#### **CUSTOMER REVIEW CREATION**

**Step 1: Customer Creates Product Review**
```http
POST /api/feedback/reviews/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "order_item_id": 1,
    "review_type": "product",
    "target_id": 1,
    "rating": 5,
    "review_text": "Excellent quality tomatoes! Fresh and organic as promised.",
    "is_verified_purchase": true,
    "review_photos": [
        "https://example.com/review-photo1.jpg"
    ]
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "review_id": 1,
    "review_type": "product",
    "target": {
        "product_id": 1,
        "product_name": "Organic Tomatoes"
    },
    "rating": 5,
    "review_text": "Excellent quality tomatoes! Fresh and organic as promised.",
    "is_verified_purchase": true,
    "is_visible": true,
    "created_by": 2,
    "created_at": "2024-01-16T16:00:00Z",
    "helpfulness_score": 0
}
```

**Database State Change:**
- New `Review` record created
- Product rating average updated
- Review visibility set to true by default

**Step 2: Customer Creates Farmer Review**
```http
POST /api/feedback/reviews/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "review_type": "farmer",
    "target_id": 1,
    "rating": 4,
    "review_text": "Good farmer, products are always fresh. Quick to pack orders.",
    "is_verified_purchase": true
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "review_id": 2,
    "review_type": "farmer",
    "target": {
        "farmer_id": 1,
        "farmer_name": "Jane Farmer",
        "farm_name": "Green Valley Farm"
    },
    "rating": 4,
    "review_text": "Good farmer, products are always fresh. Quick to pack orders.",
    "is_verified_purchase": true,
    "created_at": "2024-01-16T16:05:00Z"
}
```

**Step 3: Customer Creates Rider Review**
```http
POST /api/feedback/reviews/
Authorization: Bearer {customer_jwt_token}
Content-Type: application/json

{
    "review_type": "rider",
    "target_id": 1,
    "rating": 5,
    "review_text": "Excellent delivery service! On time and professional.",
    "is_verified_purchase": true
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "review_id": 3,
    "review_type": "rider",
    "target": {
        "rider_id": 1,
        "rider_name": "Mike Rider"
    },
    "rating": 5,
    "review_text": "Excellent delivery service! On time and professional.",
    "is_verified_purchase": true,
    "created_at": "2024-01-16T16:10:00Z"
}
```

#### **PUBLIC REVIEW ACCESS**

**Step 4: Public Views Product Reviews**
```http
GET /api/feedback/reviews/?product_id=1&review_type=product
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "review_id": 1,
            "rating": 5,
            "review_text": "Excellent quality tomatoes! Fresh and organic as promised.",
            "reviewer_name": "John D.",
            "is_verified_purchase": true,
            "created_at": "2024-01-16T16:00:00Z",
            "helpfulness_votes": 0
        }
    ],
    "count": 1,
    "average_rating": 5.0,
    "rating_distribution": {
        "5": 1,
        "4": 0,
        "3": 0,
        "2": 0,
        "1": 0
    }
}
```

#### **ADMIN MODERATION**

**Step 5: Admin Lists All Reviews**
```http
GET /api/feedback/reviews/?include_moderated=true
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "review_id": 1,
            "review_type": "product",
            "target_name": "Organic Tomatoes",
            "rating": 5,
            "review_text": "Excellent quality tomatoes! Fresh and organic as promised.",
            "reviewer": {
                "user_id": 2,
                "name": "John Doe"
            },
            "is_visible": true,
            "moderation_status": "approved",
            "created_at": "2024-01-16T16:00:00Z"
        },
        {
            "review_id": 2,
            "review_type": "farmer",
            "target_name": "Jane Farmer",
            "rating": 4,
            "is_visible": true,
            "moderation_status": "pending"
        }
    ],
    "count": 3
}
```

**Step 6: Admin Moderates Review (Hide)**
```http
PATCH /api/feedback/reviews/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "is_visible": false,
    "moderation_reason": "Contains inappropriate language",
    "moderated_by": 1,
    "moderated_at": "2024-01-16T17:00:00Z",
    "moderation_notes": "Review contains profanity - hidden from public view"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "review_id": 1,
    "is_visible": false,
    "moderation_status": "hidden",
    "moderation_reason": "Contains inappropriate language",
    "moderated_by": {
        "user_id": 1,
        "name": "Admin User"
    },
    "moderated_at": "2024-01-16T17:00:00Z",
    "updated_at": "2024-01-16T17:00:00Z"
}
```

**Database State Change:**
- `Review.is_visible` = `false`
- `Review.moderation_status` = `'hidden'`
- Product rating average recalculated
- Moderation audit log created

#### **MODERATION VERIFICATION**

**Step 7: Public Views Reviews After Moderation**
```http
GET /api/feedback/reviews/?product_id=1&review_type=product
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [],
    "count": 0,
    "average_rating": null,
    "rating_distribution": {
        "5": 0,
        "4": 0,
        "3": 0,
        "2": 0,
        "1": 0
    }
}
```

**Security Validation:**
- Moderated review not visible to public
- Rating calculations updated
- Original reviewer notified of moderation

---

## 💰 Test Scenario 5: Payouts (Admin View)

### **Goal**
Validate payout record creation, management, and proper access controls.

### **Pre-conditions**
- Completed and delivered order
- Authenticated admin, farmer, and rider users
- Payout calculation system configured

---

### **Detailed Step-by-Step API Interactions**

#### **ADMIN PAYOUT CREATION**

**Step 1: Admin Creates Farmer Payout**
```http
POST /api/finance/payouts/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "recipient_id": 1,
    "recipient_type": "farmer",
    "order_id": 1,
    "amount": 800.00,
    "payout_method": "bank_transfer",
    "payout_status": "pending",
    "calculation_details": {
        "gross_amount": 1000.00,
        "platform_fee_rate": 0.15,
        "platform_fee": 150.00,
        "tax_deduction": 50.00,
        "net_amount": 800.00
    },
    "payout_date": "2024-01-16",
    "bank_details": {
        "account_number": "1234567890",
        "bank_code": "KCBL",
        "account_name": "Jane Farmer"
    }
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "payout_id": 1,
    "payout_reference": "PAY_FRM_20240116_001",
    "recipient": {
        "user_id": 1,
        "name": "Jane Farmer",
        "user_type": "farmer"
    },
    "order": {
        "order_id": 1,
        "order_date": "2024-01-15T10:00:00Z"
    },
    "amount": "800.00",
    "payout_method": "bank_transfer",
    "payout_status": "pending",
    "calculation_details": {
        "gross_amount": "1000.00",
        "platform_fee": "150.00",
        "tax_deduction": "50.00",
        "net_amount": "800.00"
    },
    "created_at": "2024-01-16T18:00:00Z",
    "estimated_completion": "2024-01-18T12:00:00Z"
}
```

**Database State Change:**
- New `Payout` record created
- Payout reference auto-generated
- Financial audit trail initiated

**Step 2: Admin Creates Rider Payout**
```http
POST /api/finance/payouts/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "recipient_id": 1,
    "recipient_type": "rider",
    "order_id": 1,
    "amount": 200.00,
    "payout_method": "mobile_money",
    "payout_status": "pending",
    "calculation_details": {
        "base_delivery_fee": 150.00,
        "distance_bonus": 30.00,
        "customer_tip": 20.00,
        "total_amount": 200.00
    },
    "payout_date": "2024-01-16",
    "mobile_money_details": {
        "phone_number": "0798765432",
        "provider": "M-Pesa"
    }
}
```

**Expected Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "payout_id": 2,
    "payout_reference": "PAY_RDR_20240116_001",
    "recipient": {
        "user_id": 1,
        "name": "Mike Rider",
        "user_type": "rider"
    },
    "amount": "200.00",
    "payout_method": "mobile_money",
    "payout_status": "pending",
    "created_at": "2024-01-16T18:05:00Z"
}
```

#### **ADMIN PAYOUT MANAGEMENT**

**Step 3: Admin Lists All Payouts**
```http
GET /api/finance/payouts/?status=all&page=1&limit=20
Authorization: Bearer {admin_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "payout_id": 1,
            "payout_reference": "PAY_FRM_20240116_001",
            "recipient_name": "Jane Farmer",
            "recipient_type": "farmer",
            "amount": "800.00",
            "payout_method": "bank_transfer",
            "payout_status": "pending",
            "created_at": "2024-01-16T18:00:00Z"
        },
        {
            "payout_id": 2,
            "payout_reference": "PAY_RDR_20240116_001",
            "recipient_name": "Mike Rider",
            "recipient_type": "rider",
            "amount": "200.00",
            "payout_method": "mobile_money",
            "payout_status": "pending",
            "created_at": "2024-01-16T18:05:00Z"
        }
    ],
    "count": 2,
    "summary": {
        "total_pending": "1000.00",
        "total_completed": "0.00",
        "pending_count": 2
    }
}
```

#### **RECIPIENT ACCESS VALIDATION**

**Step 4: Farmer Views Own Payouts**
```http
GET /api/finance/payouts/my-payouts/
Authorization: Bearer {farmer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "payout_id": 1,
            "payout_reference": "PAY_FRM_20240116_001",
            "amount": "800.00",
            "payout_method": "bank_transfer",
            "payout_status": "pending",
            "order": {
                "order_id": 1,
                "customer_name": "John Doe"
            },
            "created_at": "2024-01-16T18:00:00Z",
            "estimated_completion": "2024-01-18T12:00:00Z"
        }
    ],
    "count": 1,
    "total_earnings": "800.00"
}
```

**Step 5: Rider Views Own Payouts**
```http
GET /api/finance/payouts/my-payouts/
Authorization: Bearer {rider_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "results": [
        {
            "payout_id": 2,
            "payout_reference": "PAY_RDR_20240116_001",
            "amount": "200.00",
            "payout_method": "mobile_money",
            "payout_status": "pending",
            "created_at": "2024-01-16T18:05:00Z"
        }
    ],
    "count": 1,
    "total_earnings": "200.00"
}
```

#### **SECURITY TESTING**

**Step 6: Customer Attempts Unauthorized Payout Access**
```http
GET /api/finance/payouts/
Authorization: Bearer {customer_jwt_token}
```

**Expected Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "detail": "You do not have permission to view payout information",
    "error_code": "payout_access_denied",
    "required_roles": ["admin", "farmer", "rider"]
}
```

#### **PAYOUT COMPLETION**

**Step 7: Admin Updates Payout Status**
```http
PATCH /api/finance/payouts/1/
Authorization: Bearer {admin_jwt_token}
Content-Type: application/json

{
    "payout_status": "completed",
    "transaction_reference": "TXN_BNK_001234567",
    "completed_at": "2024-01-17T10:30:00Z",
    "admin_notes": "Payment processed successfully via bank transfer",
    "bank_confirmation": "CONFIRMED_2024011710305678"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "payout_id": 1,
    "payout_status": "completed",
    "transaction_reference": "TXN_BNK_001234567",
    "completed_at": "2024-01-17T10:30:00Z",
    "processing_time_hours": 16.5,
    "updated_at": "2024-01-17T10:30:00Z"
}
```

**Database State Change:**
- `Payout.payout_status` = `'completed'`
- `Payout.completed_at` timestamp set
- Financial audit trail updated
- Recipient notification triggered

---

## 🔧 Implementation Notes

### **Required Pytest Fixtures**
- `admin_client` - Authenticated admin API client
- `customer_client` - Authenticated customer API client
- `farmer_client` - Authenticated farmer API client
- `rider_client` - Authenticated rider API client
- `db_reset` - Database cleanup between tests
- `create_test_data` - Comprehensive test data setup

### **API Endpoint Patterns to Test**
- `/api/core/settings/` - System configuration management
- `/api/data_insights/market-prices/` - Market data management
- `/api/communication/weather-alerts/` - Weather information
- `/api/communication/support-tickets/` - Customer support
- `/api/feedback/reviews/` - Review and rating system
- `/api/finance/payouts/` - Financial operations

### **Security Validation Requirements**
- **401 Unauthorized** - Missing/invalid JWT token
- **403 Forbidden** - Valid token, insufficient permissions
- **404 Not Found** - Resource doesn't exist or not accessible
- **400 Bad Request** - Invalid data, validation errors

### **Database State Validation**
- System settings version control
- Market price history maintenance
- Support ticket status progression
- Review moderation audit trails
- Payout transaction records

This comprehensive test specification ensures thorough validation of all administrative and management workflows with detailed API interactions, security testing, and business logic verification across the entire Vegas Inc marketplace platform. 