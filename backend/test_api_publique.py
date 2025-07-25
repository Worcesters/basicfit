#!/usr/bin/env python
"""
Test de l'API de recommandation maintenant publique
"""

import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine
from apps.machines.models import Machine
from apps.users.models import User

def test_api_publique():
    print("🌐 TEST API RECOMMANDATION PUBLIQUE")
    print("=" * 50)

    RAILWAY_URL = "https://basicfit-production.up.railway.app"

    # Test sans authentification (comme l'app Android)
    print("🔍 Test SANS authentification (comme Android):")

    try:
        # Test par ID
        url_id = f"{RAILWAY_URL}/api/workouts/recommendation/1/"
        response = requests.get(url_id, timeout=10)
        print(f"   URL ID: {url_id}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            poids = data.get('poids_recommande', 0)
            print(f"   ✅ Recommandation par ID: {poids}kg")
            print(f"   📊 Détails: {data}")
        else:
            print(f"   ❌ Erreur par ID: {response.status_code}")
            print(f"   Contenu: {response.text}")

    except Exception as e:
        print(f"   ❌ Erreur par ID: {e}")

    try:
        # Test par nom
        machine_name = "Développé%20couché"  # Encoder les espaces
        url_name = f"{RAILWAY_URL}/api/workouts/recommendation/{machine_name}/"
        response = requests.get(url_name, timeout=10)
        print(f"   URL Nom: {url_name}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            poids = data.get('poids_recommande', 0)
            print(f"   ✅ Recommandation par nom: {poids}kg")
            print(f"   📊 Détails: {data}")
        else:
            print(f"   ❌ Erreur par nom: {response.status_code}")
            print(f"   Contenu: {response.text}")

    except Exception as e:
        print(f"   ❌ Erreur par nom: {e}")

def diagnostiquer_android():
    print(f"\n📱 DIAGNOSTIC ANDROID:")
    print("=" * 50)

    print("🎯 MAINTENANT QUE L'API EST PUBLIQUE:")
    print("   ✅ L'app Android peut accéder à l'API sans authentification")
    print("   ✅ L'API devrait retourner les vraies recommandations")
    print("   ✅ Le problème 17kg devrait être résolu")

    print(f"\n🔍 VÉRIFICATIONS À FAIRE:")
    print("   1. Tester l'app Android pour voir si elle récupère les recommandations")
    print("   2. Vérifier que le fallback local n'est plus utilisé")
    print("   3. S'assurer que les recommandations sont cohérentes")

    print(f"\n💡 SI LE PROBLÈME PERSISTE:")
    print("   - Vérifier les logs Android pour les erreurs réseau")
    print("   - Vérifier que l'app utilise la bonne URL")
    print("   - Vérifier que le fallback local n'est pas hardcodé")

if __name__ == "__main__":
    test_api_publique()
    diagnostiquer_android()

    print(f"\n" + "=" * 50)
    print("✅ TEST TERMINÉ")
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Déployer les changements sur Railway")
    print("   2. Tester l'app Android")
    print("   3. Vérifier que le problème 17kg est résolu")