#!/usr/bin/env python
"""
Test de l'API de recommandation
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

def test_api_recommendation():
    print("🧪 TEST API RECOMMANDATION")
    print("=" * 50)

    # 1. Vérifier que le serveur fonctionne
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        print(f"✅ Serveur accessible: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur non accessible sur localhost:8000")
        print("💡 Vérifiez que le serveur Django est démarré")
        return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

    # 2. Récupérer une progression de test
    progression = ProgressionMachine.objects.filter(poids_actuel=17.0).first()
    if not progression:
        print("❌ Aucune progression 17kg trouvée")
        return False

    machine = progression.machine
    user = progression.utilisateur

    print(f"🔍 Test avec:")
    print(f"   - Machine: {machine.nom} (ID: {machine.id})")
    print(f"   - Utilisateur: {user.nom_complet}")
    print(f"   - Poids actuel: {progression.poids_actuel}kg")

    # 3. Tester l'API par ID de machine
    print(f"\n📡 TEST API PAR ID:")
    try:
        url = f"http://localhost:8000/api/workouts/recommendation/{machine.id}/"
        response = requests.get(url, timeout=10)

        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Réponse API:")
            print(f"      - Poids recommandé: {data.get('poids_recommande')}kg")
            print(f"      - Séries recommandées: {data.get('series_recommandees')}")
            print(f"      - Répétitions recommandées: {data.get('repetitions_recommandees')}")
            print(f"      - Objectif: {data.get('objectif')}")

            poids_api = data.get('poids_recommande', 0)
            if poids_api > 17.0:
                print(f"   🎯 PROGRESSION DÉTECTÉE: 17kg → {poids_api}kg")
            else:
                print(f"   ⏸️ MAINTIEN: {poids_api}kg")

        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   Contenu: {response.text}")

    except Exception as e:
        print(f"   ❌ Erreur requête: {e}")

    # 4. Tester l'API par nom de machine
    print(f"\n📡 TEST API PAR NOM:")
    try:
        machine_name = machine.nom.replace(" ", "%20")  # Encoder les espaces
        url = f"http://localhost:8000/api/workouts/recommendation/{machine_name}/"
        response = requests.get(url, timeout=10)

        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Réponse API:")
            print(f"      - Poids recommandé: {data.get('poids_recommande')}kg")
            print(f"      - Séries recommandées: {data.get('series_recommandees')}")
            print(f"      - Répétitions recommandées: {data.get('repetitions_recommandees')}")

        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   Contenu: {response.text}")

    except Exception as e:
        print(f"   ❌ Erreur requête: {e}")

    # 5. Tester la méthode backend directement
    print(f"\n🔧 TEST BACKEND DIRECT:")
    try:
        recommandation_backend = progression.calculer_recommandation_intelligente()
        print(f"   ✅ Backend direct: {recommandation_backend}kg")

        if recommandation_backend > 17.0:
            print(f"   🎯 PROGRESSION BACKEND: 17kg → {recommandation_backend}kg")
        else:
            print(f"   ⏸️ MAINTIEN BACKEND: {recommandation_backend}kg")

    except Exception as e:
        print(f"   ❌ Erreur backend: {e}")

    return True

def test_android_simulation():
    print(f"\n📱 SIMULATION ANDROID:")
    print("=" * 50)

    # Simuler ce que fait l'app Android
    progression = ProgressionMachine.objects.filter(poids_actuel=17.0).first()
    if not progression:
        return

    machine = progression.machine

    print(f"🔍 Simulation appel API Android:")
    print(f"   - Machine: {machine.nom}")
    print(f"   - URL attendue: http://localhost:8000/api/workouts/recommendation/{machine.id}/")

    try:
        # Simuler l'appel Android
        url = f"http://localhost:8000/api/workouts/recommendation/{machine.id}/"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            poids_api = data.get('poids_recommande', 0)

            print(f"   ✅ API répond: {poids_api}kg")

            # Simuler la logique Android
            if poids_api > 0:
                print(f"   📱 Android devrait afficher: {poids_api}kg")
            else:
                print(f"   📱 Android devrait utiliser le fallback (20kg)")

        else:
            print(f"   ❌ API ne répond pas: {response.status_code}")
            print(f"   📱 Android devrait utiliser le fallback (20kg)")

    except Exception as e:
        print(f"   ❌ Erreur réseau: {e}")
        print(f"   📱 Android devrait utiliser le fallback (20kg)")

if __name__ == "__main__":
    success = test_api_recommendation()
    if success:
        test_android_simulation()

    print(f"\n" + "=" * 50)
    print("✅ TEST TERMINÉ")