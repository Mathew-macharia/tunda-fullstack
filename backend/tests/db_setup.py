"""
Database setup and management for E2E testing.
Run this script to setup, reset, or cleanup the E2E test database.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from core.models import SystemSettings


def create_test_database():
    """Create and setup test database"""
    print("🚀 Setting up E2E test database...")
    
    # Create test database using Django's test runner
    settings.DATABASES['default']['NAME'] = 'test_tunda_e2e'
    
    try:
        # Run migrations
        call_command('migrate', verbosity=1, interactive=False)
        print("✅ Database migrations completed")
        
        # Initialize system settings
        SystemSettings.objects.initialize_default_settings()
        print("✅ System settings initialized")
        
        print("🎉 E2E test database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False


def cleanup_test_data():
    """Remove all test data while preserving schema"""
    print("🧹 Cleaning up test data...")
    
    # Set test database
    settings.DATABASES['default']['NAME'] = 'test_tunda_e2e'
    
    try:
        # Import models
        from users.models import User
        from locations.models import Location
        from farms.models import Farm
        from products.models import Product, ProductCategory, ProductListing
        from carts.models import Cart, CartItem
        from orders.models import Order, OrderItem
        
        # Delete data in correct order
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        ProductListing.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Farm.objects.all().delete()
        Location.objects.all().delete()
        User.objects.all().delete()
        
        # Reinitialize system settings
        if not SystemSettings.objects.exists():
            SystemSettings.objects.initialize_default_settings()
        
        print("✅ Test data cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up data: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tests/db_setup.py [setup|cleanup]")
        print("  setup   - Create and initialize test database")
        print("  cleanup - Remove all test data")
        return
        
    command = sys.argv[1].lower()
    
    if command == "setup":
        success = create_test_database()
    elif command == "cleanup":
        success = cleanup_test_data()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, cleanup")
        return
        
    if success:
        print("✅ Operation completed successfully")
    else:
        print("❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 