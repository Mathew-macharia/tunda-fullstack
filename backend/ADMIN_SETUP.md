# 🛠️ Vegas Inc - Admin Account Setup Guide

This guide explains how to set up and manage admin accounts for your Vegas Inc application.

## 📋 Overview

Vegas Inc uses a **hybrid admin approach** with two different admin interfaces:

### 🔧 Django Admin Interface
- **URL**: `http://localhost:8000/django-admin/`
- **Purpose**: Technical management, debugging, system maintenance
- **Users**: Developers, technical staff
- **Features**: Direct database access, model management, system debugging

### 🎯 Custom Admin Interface  
- **URL**: `http://localhost:5173/admin`
- **Purpose**: Business operations, user management, daily tasks
- **Users**: Business managers, operators, customer service
- **Features**: User-friendly dashboards, reports, business workflows

## 🚀 Quick Setup

### Method 1: Using the Setup Script (Recommended)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux

# Run the admin setup script
python create_admin.py
```

The script will guide you through creating both types of admin accounts.

### Method 2: Manual Setup

#### Create Django Superuser
```bash
python manage.py createsuperuser
```

#### Create Custom Admin User
```bash
python manage.py shell
```

Then in the Python shell:
```python
from users.models import User

# Create admin user
admin_user = User.objects.create_user(
    phone_number='+254712345678',  # Replace with actual phone
    password='your_secure_password',
    first_name='Admin',
    last_name='User',
    email='admin@vegas.com',
    user_role='admin',
    is_staff=True,
    is_superuser=True,
    is_active=True,
)

print(f"Admin user created: {admin_user.phone_number}")
```

## 🔐 Admin Account Types

### Django Superuser
- **Access**: Django Admin (`/django-admin/`)
- **Permissions**: Full database access
- **Use Cases**:
  - Database debugging
  - Model management
  - System maintenance
  - Emergency fixes
  - Developer testing

### Custom Admin User
- **Access**: Custom Admin Interface (`/admin`)
- **Permissions**: Business-level admin access
- **Use Cases**:
  - User management
  - Order management
  - Payment oversight
  - System settings
  - Reports and analytics

## 🎯 Admin Interface Features

### Custom Admin Dashboard (`/admin`)
- **Dashboard**: `/admin` - Overview with key metrics
- **Users**: `/admin/users` - Manage farmers, consumers, riders
- **Orders**: `/admin/orders` - Order management and oversight
- **Reviews**: `/admin/reviews` - Review moderation
- **Payouts**: `/admin/payouts` - Financial management
- **Settings**: `/admin/settings` - System configuration

### Django Admin (`/django-admin/`)
- Full model CRUD operations
- User permissions management
- Database query interface
- System logs and debugging
- Advanced filtering and search

## 🔒 Security Best Practices

### Account Creation
- ✅ **Never** allow admin account creation through public registration
- ✅ Use the setup script or command line only
- ✅ Create admin accounts manually for each administrator
- ✅ Use strong, unique passwords

### Access Control
- ✅ Django Admin: Only for technical staff
- ✅ Custom Admin: For business operations staff
- ✅ Regular password rotation
- ✅ Monitor admin activity logs

### URL Security
- ✅ Django Admin at `/django-admin/` (not the default `/admin/`)
- ✅ Custom Admin at `/admin/` for business users
- ✅ Consider changing URLs in production
- ✅ Use HTTPS in production

## 🌐 Access URLs

### Development
- **Django Admin**: http://localhost:8000/django-admin/
- **Custom Admin**: http://localhost:5173/admin
- **API**: http://localhost:8000/api/

### Production
- **Django Admin**: https://yourdomain.com/django-admin/
- **Custom Admin**: https://yourdomain.com/admin
- **API**: https://yourdomain.com/api/

## 🛠️ Troubleshooting

### Can't Access Django Admin
1. Check if superuser was created: `python manage.py shell`
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   print(User.objects.filter(is_superuser=True))
   ```

2. Create superuser: `python manage.py createsuperuser`

3. Check URL: Should be `/django-admin/` not `/admin/`

### Can't Access Custom Admin
1. Check if user has `user_role='admin'`
2. Verify user is active: `is_active=True`
3. Check frontend routing configuration
4. Verify authentication token

### Common Issues
- **Port conflicts**: Django (8000) vs Frontend (5173)
- **URL conflicts**: Fixed by using `/django-admin/` vs `/admin/`
- **Permission issues**: Check `user_role` and `is_staff` flags
- **Database connection**: Verify MySQL is running

## 📚 Related Files

- `backend/create_admin.py` - Admin setup script
- `backend/tunda/urls.py` - URL configuration
- `frontend/src/router/index.js` - Frontend routing
- `frontend/src/views/admin/` - Admin interface components

## 🤝 Support

If you encounter issues:
1. Check this documentation
2. Review error logs in Django admin
3. Check browser console for frontend issues
4. Verify database connections
5. Ensure virtual environment is activated

---

**Last Updated**: $(date)
**Version**: 1.0 