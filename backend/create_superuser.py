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
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print(f"Superuser password updated: {user.username}")
except User.DoesNotExist:
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            prenom='Admin',
            nom='Admin'
        )
        print(f"Superuser created successfully: {user.username}")
    except Exception as e:
        print(f"Error creating superuser: {e}")