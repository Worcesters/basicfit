#!/usr/bin/env python
"""
Test de l'API Railway de production
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

def test_api_railway():
    print("🌐 TEST API RAILWAY PRODUCTION")
    print("=" * 50)

    # URL de l'API Railway utilisée par Android
    RAILWAY_URL = "https://basicfit-production.up.railway.app"

    print(f"🔍 Test de l'API Railway: {RAILWAY_URL}")

    # 1. Test de base - Page d'accueil
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"✅ Serveur Railway accessible: {response.status_code}")
        if response.status_code == 200:
            print(f"   Contenu: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Railway non accessible")
        print("💡 Vérifiez l'URL Railway et que le service est actif")
        return False
    except Exception as e:
        print(f"❌ Erreur connexion Railway: {e}")
        return False

    # 2. Test de l'API workouts
    try:
        response = requests.get(f"{RAILWAY_URL}/api/workouts/", timeout=10)
        print(f"📡 API Workouts: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ API Workouts fonctionne")
        else:
            print(f"   ❌ Erreur API Workouts: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur API Workouts: {e}")

    # 3. Test de l'API machines
    try:
        response = requests.get(f"{RAILWAY_URL}/api/machines/", timeout=10)
        print(f"🏋️ API Machines: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            machines_count = len(data.get('results', []))
            print(f"   ✅ API Machines fonctionne ({machines_count} machines)")
        else:
            print(f"   ❌ Erreur API Machines: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur API Machines: {e}")

    # 4. Test de l'API recommandation (avec une machine existante)
    try:
        # Récupérer une machine de test depuis la BDD locale
        machine = Machine.objects.filter(nom__icontains="Développé").first()
        if machine:
            print(f"\n🎯 TEST RECOMMANDATION:")
            print(f"   Machine test: {machine.nom} (ID: {machine.id})")

            # Test par ID
            url_id = f"{RAILWAY_URL}/api/workouts/recommendation/{machine.id}/"
            response = requests.get(url_id, timeout=10)
            print(f"   URL ID: {url_id}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                poids_api = data.get('poids_recommande', 0)
                print(f"   ✅ Recommandation API: {poids_api}kg")

                if poids_api > 0:
                    print(f"   🎯 API fonctionne correctement")
                else:
                    print(f"   ⚠️ API répond mais poids = 0 (pas de progression)")
            else:
                print(f"   ❌ Erreur API: {response.status_code}")
                print(f"   Contenu: {response.text}")

            # Test par nom
            machine_name = machine.nom.replace(" ", "%20")
            url_name = f"{RAILWAY_URL}/api/workouts/recommendation/{machine_name}/"
            response = requests.get(url_name, timeout=10)
            print(f"   URL Nom: {url_name}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                poids_api = data.get('poids_recommande', 0)
                print(f"   ✅ Recommandation par nom: {poids_api}kg")
            else:
                print(f"   ❌ Erreur par nom: {response.status_code}")
        else:
            print("❌ Aucune machine trouvée pour le test")

    except Exception as e:
        print(f"   ❌ Erreur test recommandation: {e}")

def diagnostiquer_probleme_android():
    print(f"\n📱 DIAGNOSTIC PROBLÈME ANDROID:")
    print("=" * 50)

    print("🔍 CAUSES POSSIBLES DU PROBLÈME 17KG:")
    print("   1. ❌ L'app Android ne peut pas se connecter à Railway")
    print("   2. ❌ L'API Railway ne retourne pas de données")
    print("   3. ❌ Pas de progression 17kg dans la BDD Railway")
    print("   4. ❌ L'app Android utilise le fallback local (20kg)")
    print("   5. ❌ Problème d'authentification/authorization")

    print(f"\n💡 SOLUTIONS À VÉRIFIER:")
    print("   🔧 1. Vérifier l'URL Railway dans l'app Android")
    print("   🔧 2. Vérifier que Railway est actif et accessible")
    print("   🔧 3. Vérifier les logs Android pour les erreurs réseau")
    print("   🔧 4. Vérifier les données de progression dans Railway")
    print("   🔧 5. Tester l'API Railway directement")

def verifier_configuration_android():
    print(f"\n⚙️ CONFIGURATION ANDROID À VÉRIFIER:")
    print("=" * 50)

    print("📱 Dans l'app Android, vérifiez:")
    print("   1. L'URL de l'API dans ApiService.kt")
    print("      - Doit pointer vers Railway, pas localhost")
    print("      - Exemple: https://basicfit-api-production.up.railway.app")

    print("   2. Les logs de connexion")
    print("      - Vérifier les erreurs réseau")
    print("      - Vérifier les timeouts")

    print("   3. Le fallback local")
    print("      - Si l'API échoue, l'app utilise 20kg")
    print("      - C'est probablement ce qui se passe")

if __name__ == "__main__":
    test_api_railway()
    diagnostiquer_probleme_android()
    verifier_configuration_android()

    print(f"\n" + "=" * 50)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Remplacer RAILWAY_URL par votre vraie URL")
    print("   2. Exécuter le test pour vérifier l'API Railway")
    print("   3. Vérifier la configuration Android")
    print("   4. Corriger l'URL ou les données selon le diagnostic")