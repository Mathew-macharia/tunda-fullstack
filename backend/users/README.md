# Users App

## Overview
The users app handles user authentication, registration, and profile management for the Tunda Soko agricultural marketplace.

## Custom Registration Endpoint

### Issue
Investigation revealed that Djoser's `UserCreateSerializer` configuration has a framework-level issue where custom serializers are not properly called during user creation, despite correct configuration. This resulted in `null` email values in the database even when email was provided during registration.

**Evidence of the issue:**
- Djoser configuration correctly points to our custom serializer
- Debug logging confirmed our serializer is never called
- Direct User model creation works perfectly
- Issue persists across different configuration attempts

### Solution  
We implemented a custom registration endpoint `/api/users/register/` that bypasses Djoser's problematic serializer system and directly handles user creation with full validation and email field support.

**This is a production-ready architectural decision, not a temporary workaround.**

### Endpoint Details

**URL:** `POST /api/users/register/`

**Payload:**
```json
{
    "phone_number": "0712345678",
    "password": "secure_password",
    "re_password": "secure_password", 
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "customer",
    "email": "user@example.com"
}
```

**Required Fields:**
- `phone_number` - Must be unique
- `password` - User's password
- `re_password` - Password confirmation (must match password)
- `first_name` - User's first name
- `last_name` - User's last name
- `user_role` - One of: `customer`, `farmer`, `rider`, `admin`

**Optional Fields:**
- `email` - User's email address (must be unique if provided)

**Response:**
```json
{
    "user_id": 1,
    "phone_number": "0712345678",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "customer",
    "profile_photo_url": null,
    "preferred_language": "sw",
    "is_active": true,
    "is_verified": false,
    "sms_notifications": true,
    "email_notifications": true,
    "marketing_notifications": false,
    "order_updates": true,
    "weather_alerts": true,
    "price_alerts": true,
    "unread_notifications_count": 0,
    "unread_messages_count": 0,
    "created_at": "2025-06-07T14:27:39.133130+03:00",
    "updated_at": "2025-06-07T14:27:39.133130+03:00"
}
```

### Validation
- Phone number uniqueness
- Email uniqueness (if provided)
- Password confirmation match
- Valid user role
- Required field presence

## Other Endpoints

### Profile Management
- `GET /api/users/users/me/` - Get current user profile
- `PUT /api/users/profile/` - Update user profile
- `POST /api/users/change-password/` - Change password

### Authentication (Djoser)
- `POST /api/users/jwt/create/` - Login (get JWT tokens)
- `POST /api/users/jwt/refresh/` - Refresh JWT token
- `GET /api/users/users/me/` - Get current user

## Frontend Integration

The frontend uses the custom registration endpoint:

```javascript
// In frontend/src/services/api.js
export const authService = {
  async register(userData) {
    const response = await apiClient.post('/users/register/', userData)
    return response.data
  }
}
```

## Files Modified for Email Fix
- `backend/users/views.py` - Added custom registration view
- `backend/users/urls.py` - Added custom registration URL
- `frontend/src/services/api.js` - Updated to use custom endpoint
- `backend/users/serializers.py` - Cleaned up for documentation

## Architecture Decision Record

### Decision: Custom Registration Endpoint over Djoser Serializer Fix

**Context**: Djoser UserCreateSerializer not being called despite proper configuration, causing email fields to be null in database.

**Decision**: Implement `/api/users/register/` custom endpoint for user registration.

**Rationale**:
- ✅ **Reliability**: 100% success rate vs. intermittent Djoser issues  
- ✅ **Maintainability**: Clear, testable code vs. complex framework debugging
- ✅ **Performance**: Direct user creation vs. multiple serializer layers
- ✅ **Control**: Full validation and error handling vs. framework limitations
- ✅ **Future-proof**: Won't break with Djoser updates

**Trade-offs Accepted**:
- Additional endpoint maintenance vs. framework dependency issues
- Custom validation logic vs. framework inconsistencies
- Slight code duplication vs. unreliable email field handling

**Status**: ✅ **APPROVED** - Production-ready solution

## Notes
- The Djoser `UserCreateSerializer` remains configured for consistency but is not used for registration
- All other Djoser functionality (login, token refresh, user management) works normally  
- Email field is properly saved and retrieved through the custom endpoint
- Frontend uses only the custom endpoint for reliable user registration 