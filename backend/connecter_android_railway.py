#!/usr/bin/env python
"""
Script pour connecter l'utilisateur Android à l'API Railway
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

def connecter_android_railway():
    print("🔐 CONNEXION ANDROID À RAILWAY")
    print("=" * 50)

    RAILWAY_URL = "https://basicfit-production.up.railway.app"

    # 1. Créer un utilisateur de test dans Railway
    print("👤 Création utilisateur de test:")

    try:
        # Essayer de créer un compte
        register_url = f"{RAILWAY_URL}/api/users/android/register/"
        register_data = {
            "email": "android_test@example.com",
            "password": "android123",
            "nom": "Android",
            "prenom": "Test",
            "objectif_sportif": "prise de masse",
            "niveau_experience": "intermediaire"
        }

        register_response = requests.post(register_url, json=register_data, timeout=10)
        print(f"   Tentative d'inscription: {register_response.status_code}")

        if register_response.status_code == 201 or register_response.status_code == 200:
            print(f"   ✅ Utilisateur créé ou existe déjà")
        else:
            print(f"   ❌ Erreur inscription: {register_response.text}")

    except Exception as e:
        print(f"   ❌ Erreur inscription: {e}")

    # 2. Se connecter pour obtenir un token
    print(f"\n🔑 Connexion pour obtenir token:")

    try:
        login_url = f"{RAILWAY_URL}/api/users/android/login/"
        login_data = {
            "email": "android_test@example.com",
            "password": "android123"
        }

        login_response = requests.post(login_url, json=login_data, timeout=10)
        print(f"   Tentative de connexion: {login_response.status_code}")

        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('token')

            if token:
                print(f"   ✅ Token obtenu: {token[:20]}...")

                # 3. Tester l'API de recommandation avec le token
                print(f"\n🎯 Test recommandation avec authentification:")

                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                # Test par ID
                url_id = f"{RAILWAY_URL}/api/workouts/recommendation/1/"
                response = requests.get(url_id, headers=headers, timeout=10)
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

                # Test par nom
                machine_name = "Développé%20couché"
                url_name = f"{RAILWAY_URL}/api/workouts/recommendation/{machine_name}/"
                response = requests.get(url_name, headers=headers, timeout=10)
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

                return token
            else:
                print(f"   ❌ Pas de token dans la réponse")
                return None
        else:
            print(f"   ❌ Échec de connexion: {login_response.status_code}")
            print(f"   Contenu: {login_response.text}")
            return None

    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return None

def instructions_android():
    print(f"\n📱 INSTRUCTIONS POUR ANDROID:")
    print("=" * 50)

    print("🔧 POUR RÉSOUDRE LE PROBLÈME 17KG:")
    print("   1. Dans l'app Android, allez dans les paramètres")
    print("   2. Trouvez l'option de connexion/déconnexion")
    print("   3. Connectez-vous avec:")
    print("      - Email: android_test@example.com")
    print("      - Mot de passe: android123")
    print("   4. Ou créez un nouveau compte")
    print("   5. Testez une recommandation d'exercice")

    print(f"\n💡 VÉRIFICATIONS:")
    print("   - L'app doit afficher 'Connecté' ou similaire")
    print("   - Les recommandations doivent venir de l'API")
    print("   - Plus de fallback local (20kg)")

    print(f"\n🔍 SI LE PROBLÈME PERSISTE:")
    print("   - Vérifier les logs Android (Logcat)")
    print("   - Vérifier que l'URL Railway est correcte")
    print("   - Vérifier la connexion internet")

if __name__ == "__main__":
    token = connecter_android_railway()
    instructions_android()

    print(f"\n" + "=" * 50)
    print("✅ DIAGNOSTIC TERMINÉ")

    if token:
        print(f"\n🎯 TOKEN POUR TESTS:")
        print(f"   {token}")
        print(f"\n📋 COMMANDE CURL POUR TESTER:")
        print(f"   curl -H 'Authorization: Bearer {token}' https://basicfit-production.up.railway.app/api/workouts/recommendation/1/")