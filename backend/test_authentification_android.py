#!/usr/bin/env python
"""
Test d'authentification pour l'app Android
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

def test_authentification_android():
    print("🔐 TEST AUTHENTIFICATION ANDROID")
    print("=" * 50)

    RAILWAY_URL = "https://basicfit-production.up.railway.app"

    # 1. Test sans authentification (comme l'app Android si pas connectée)
    print("🔍 Test SANS authentification:")
    try:
        url = f"{RAILWAY_URL}/api/workouts/recommendation/1/"
        response = requests.get(url, timeout=10)
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 401:
            print("   ❌ Authentification requise (normal)")
            print("   💡 L'app Android doit être connectée pour utiliser l'API")
        else:
            print(f"   ✅ API accessible sans authentification")

    except Exception as e:
        print(f"   ❌ Erreur: {e}")

    # 2. Test avec authentification (simuler un utilisateur connecté)
    print(f"\n🔐 Test AVEC authentification:")

    # Créer un token de test (vous devrez adapter selon votre système d'auth)
    try:
        # D'abord, essayer de se connecter
        login_url = f"{RAILWAY_URL}/api/users/android/login/"
        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }

        login_response = requests.post(login_url, json=login_data, timeout=10)
        print(f"   Tentative de connexion: {login_response.status_code}")

        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('token')

            if token:
                print(f"   ✅ Token obtenu: {token[:20]}...")

                # Test avec le token
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                url = f"{RAILWAY_URL}/api/workouts/recommendation/1/"
                response = requests.get(url, headers=headers, timeout=10)
                print(f"   Test avec token: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    poids = data.get('poids_recommande', 0)
                    print(f"   ✅ Recommandation obtenue: {poids}kg")
                else:
                    print(f"   ❌ Erreur avec token: {response.status_code}")
                    print(f"   Contenu: {response.text}")
            else:
                print(f"   ❌ Pas de token dans la réponse")
        else:
            print(f"   ❌ Échec de connexion: {login_response.status_code}")
            print(f"   Contenu: {login_response.text}")

    except Exception as e:
        print(f"   ❌ Erreur authentification: {e}")

def diagnostiquer_probleme_android():
    print(f"\n📱 DIAGNOSTIC COMPLET ANDROID:")
    print("=" * 50)

    print("🔍 CAUSE RACINE DU PROBLÈME 17KG:")
    print("   1. ❌ L'app Android n'est pas connectée à l'API Railway")
    print("   2. ❌ L'API de recommandation nécessite une authentification")
    print("   3. ❌ Sans token valide, l'API retourne 401 (Unauthorized)")
    print("   4. ❌ L'app Android utilise le fallback local (20kg)")
    print("   5. ❌ Le fallback local est probablement mal configuré")

    print(f"\n💡 SOLUTIONS POSSIBLES:")
    print("   🔧 1. Rendre l'API de recommandation publique (sans auth)")
    print("   🔧 2. S'assurer que l'utilisateur Android est connecté")
    print("   🔧 3. Corriger le fallback local dans l'app Android")
    print("   🔧 4. Ajouter une authentification automatique")

    print(f"\n🎯 SOLUTION RECOMMANDÉE:")
    print("   Pour un test rapide, rendre l'API de recommandation publique")
    print("   Puis corriger le fallback local pour qu'il ne soit pas 20kg")

def proposer_corrections():
    print(f"\n🛠️ CORRECTIONS À APPORTER:")
    print("=" * 50)

    print("1️⃣ BACKEND - Rendre l'API publique:")
    print("   Dans backend/apps/workouts/views.py:")
    print("   - Retirer @permission_classes([IsAuthenticated])")
    print("   - Ou ajouter @permission_classes([AllowAny])")

    print("\n2️⃣ ANDROID - Corriger le fallback:")
    print("   Dans WorkoutSummaryScreen.kt:")
    print("   - Vérifier que le fallback n'est pas hardcodé à 20kg")
    print("   - Utiliser une logique plus intelligente")

    print("\n3️⃣ ANDROID - Vérifier la connexion:")
    print("   Dans MainActivity.kt:")
    print("   - S'assurer que l'utilisateur est connecté")
    print("   - Vérifier que le token est stocké")

if __name__ == "__main__":
    test_authentification_android()
    diagnostiquer_probleme_android()
    proposer_corrections()

    print(f"\n" + "=" * 50)
    print("✅ DIAGNOSTIC TERMINÉ")