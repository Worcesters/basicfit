#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser or update password
try:
    # Try to get existing user and update password
    user = User.objects.get(email='admin@example.com')
    user.set_password('admin123')
    user.save()
    print(f"Superuser password updated: {user.email}")
except User.DoesNotExist:
    # Create new superuser
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            prenom='Admin',
            nom='Admin'
        )
        print(f"Superuser created successfully: {user.email}")
    except Exception as e:
        print(f"Error creating superuser: {e}")

# Also create a simple test user
try:
    test_user = User.objects.get(email='test@example.com')
    test_user.set_password('test123')
    test_user.save()
    print(f"Test user password updated: {test_user.email}")
except User.DoesNotExist:
    try:
        test_user = User.objects.create_superuser(
            username='test',
            email='test@example.com',
            password='test123',
            prenom='Test',
            nom='User'
        )
        print(f"Test user created successfully: {test_user.email}")
    except Exception as e:
        print(f"Error creating test user: {e}")

print("\n=== IDENTIFIANTS ADMIN ===")
print("Option 1:")
print("  Email: admin@example.com")
print("  Password: admin123")
print("\nOption 2:")
print("  Email: test@example.com")
print("  Password: test123")
print("\nURL: http://127.0.0.1:8000/admin/")