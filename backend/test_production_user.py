#!/usr/bin/env python
"""
Test avec le compte production réel jeremy.didier77@gmail.com
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.workouts.simple_recommendation import get_simple_recommendation_by_name
from apps.machines.models import Machine

User = get_user_model()

# Créer ou récupérer l'utilisateur production
user, created = User.objects.get_or_create(
    email='jeremy.didier77@gmail.com',
    defaults={
        'username': 'jeremy.didier77@gmail.com',
        'first_name': 'Jeremy',
        'last_name': 'Didier'
    }
)

if created:
    user.set_password('jeremyd77')
    user.save()
    print(f"✅ Utilisateur créé: {user.email}")
else:
    print(f"✅ Utilisateur existant: {user.email}")

# Test des recommandations
print("\n=== TEST RECOMMANDATIONS ===")

# Tester Supine Press
result = get_simple_recommendation_by_name(user, "Supine Press")
print(f"\n🔍 Test Supine Press:")
print(f"  Success: {result['success']}")
if result['success']:
    data = result['data']
    print(f"  Poids: {data.get('poids_recommande')}kg")
    print(f"  Séries: {data.get('series_recommandees')}")
    print(f"  Reps: {data.get('reps_recommandees')}")
    print(f"  Source: {data.get('source')}")
    print(f"  Notes: {data.get('notes')}")
else:
    print(f"  Erreur: {result['error']}")

# Lister quelques machines
print("\n=== MACHINES DISPONIBLES ===")
machines = Machine.objects.all()[:10]
for machine in machines:
    print(f"- {machine.nom} (ID: {machine.id})")

print(f"\nTotal machines: {Machine.objects.count()}")