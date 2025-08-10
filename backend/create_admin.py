#!/usr/bin/env python
"""
Admin Account Creation Script for Vegas Inc

This script helps create admin accounts for both Django admin and custom admin interface.
Run this script to set up initial admin accounts.

Usage:
    python create_admin.py

Requirements:
    - Django project must be properly configured
    - Database must be migrated
    - Virtual environment should be activated
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User

def create_superuser_interactive():
    """Create superuser interactively using Django's built-in command"""
    print("🚀 Creating Django Superuser Account...")
    print("This account can access Django Admin at: http://localhost:8000/django-admin/")
    print("-" * 60)
    
    execute_from_command_line(['manage.py', 'createsuperuser'])

def create_admin_user():
    """Create an admin user for the custom admin interface"""
    print("\n🎯 Creating Custom Admin Account...")
    print("This account can access Custom Admin at: http://localhost:5173/admin")
    print("-" * 60)
    
    User = get_user_model()
    
    # Get user input
    phone_number = input("Enter phone number (e.g., +254712345678): ").strip()
    
    if not phone_number:
        print("❌ Phone number is required!")
        return False
    
    # Check if user already exists
    if User.objects.filter(phone_number=phone_number).exists():
        print(f"❌ User with phone number {phone_number} already exists!")
        return False
    
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    email = input("Enter email (optional): ").strip() or None
    
    # Get password
    import getpass
    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match!")
        return False
    
    try:
        # Create the admin user
        admin_user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_role='admin',  # Set as admin (correct field name)
            is_staff=True,      # Allow Django admin access
            is_superuser=True,  # Full permissions
            is_active=True,
        )
        
        print(f"✅ Admin user created successfully!")
        print(f"📱 Phone: {phone_number}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"📧 Email: {email or 'Not provided'}")
        print(f"🔑 User Role: {admin_user.user_role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

def main():
    """Main function to run the admin creation process"""
    print("=" * 70)
    print("🛠️  VEGAS INC - ADMIN ACCOUNT SETUP")
    print("=" * 70)
    print()
    print("This script will help you create admin accounts for your system.")
    print("You can create accounts for:")
    print("  1. Django Admin Interface (technical/developer access)")
    print("  2. Custom Admin Interface (business operations)")
    print()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Create Django Superuser (for /django-admin/)")
        print("2. Create Custom Admin User (for /admin/)")
        print("3. Create both accounts")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            create_superuser_interactive()
            
        elif choice == '2':
            if create_admin_user():
                print("\n✅ Custom admin account created successfully!")
            
        elif choice == '3':
            print("Creating both accounts...\n")
            create_superuser_interactive()
            print("\n" + "="*50 + "\n")
            create_admin_user()
            
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        print("\n" + "-"*50)

if __name__ == '__main__':
    main()
