#!/usr/bin/env python3
"""
Test direct des vues de recommandation
"""

import os
import sys
import django

# Configuration Django AVANT tout import
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from apps.workouts.views import get_recommendation_by_id, get_recommendation

def test_views_directly():
    print("=== TEST DIRECT DES VUES ===")
    
    factory = RequestFactory()
    
    # Test vue par ID
    print("\n1. Test vue get_recommendation_by_id...")
    request = factory.get('/api/workouts/recommendation/id/1/')
    request.user = AnonymousUser()
    
    try:
        response = get_recommendation_by_id(request, machine_id=1)
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.data}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test vue par nom
    print("\n2. Test vue get_recommendation...")
    request = factory.get('/api/workouts/recommendation/name/Supine%20Press/')
    request.user = AnonymousUser()
    
    try:
        response = get_recommendation(request, machine_name="Supine Press")
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.data}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_views_directly()