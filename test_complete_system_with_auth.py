#!/usr/bin/env python3
"""
Script de test complet du système avec authentification
Teste l'enregistrement de séances et la récupération de recommandations
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

def create_test_user():
    """Crée un utilisateur de test s'il n'existe pas"""
    try:
        # Essayer de créer l'utilisateur via l'admin Django ou un superuser
        print("ℹ️ Création d'un utilisateur de test via l'admin Django...")
        print("   Veuillez créer manuellement un utilisateur 'testuser' avec le mot de passe 'testpass123'")
        print("   ou utiliser la commande: python manage.py createsuperuser")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return False

def get_auth_token():
    """Récupère un token d'authentification via JWT"""
    try:
        auth_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

        # Utiliser l'endpoint JWT qui ne nécessite pas CSRF
        response = requests.post(f"{BASE_URL}/users/token/", json=auth_data)

        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            if token:
                print("✅ Token d'authentification obtenu")
                return token
            else:
                print("❌ Token non trouvé dans la réponse")
                return None
        else:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erreur lors de l'authentification: {e}")
        return None

def test_workout_registration(token):
    """Teste l'enregistrement d'une séance complète"""
    print("\n📝 Test 1: Enregistrement d'une séance complète...")

    # Données de test pour une séance
    workout_data = {
        "nom_seance": "Test Séance Complète",
        "date_seance": datetime.now().strftime("%Y-%m-%d"),
        "duree_minutes": 45,
        "exercices": [
            {
                "nom_machine": "Presse à cuisses",
                "poids": 80.0,
                "repetitions": 12,
                "series": 3,
                "repos_secondes": 90
            },
            {
                "nom_machine": "Développé couché",
                "poids": 60.0,
                "repetitions": 10,
                "series": 4,
                "repos_secondes": 120
            },
            {
                "nom_machine": "Traction assistée",
                "poids": 40.0,
                "repetitions": 8,
                "series": 3,
                "repos_secondes": 60
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{BASE_URL}/workouts/register-complete/",
                               json=workout_data, headers=headers)

        if response.status_code == 201:
            print("✅ Séance enregistrée avec succès")
            data = response.json()
            print(f"   ID de la séance: {data.get('id')}")
            print(f"   Nombre d'exercices: {len(data.get('exercices', []))}")
            return True
        else:
            print(f"❌ Erreur lors de l'enregistrement: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement: {e}")
        return False

def test_recommendation_retrieval(token):
    """Teste la récupération de recommandations"""
    print("\n🔮 Test 2: Récupération de recommandations...")

    # D'abord, récupérer la liste des machines
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Récupérer les machines
        response = requests.get(f"{BASE_URL}/machines/", headers=headers)

        if response.status_code == 200:
            machines = response.json()
            if machines:
                # Tester avec la première machine
                machine_id = machines[0]['id']
                machine_name = machines[0]['nom']

                print(f"   Test avec la machine: {machine_name} (ID: {machine_id})")

                # Récupérer la recommandation
                reco_response = requests.get(f"{BASE_URL}/workouts/recommendation/{machine_id}/",
                                          headers=headers)

                if reco_response.status_code == 200:
                    reco_data = reco_response.json()
                    print("✅ Recommandation récupérée avec succès")
                    print(f"   Poids recommandé: {reco_data.get('poids_recommande')}kg")
                    print(f"   Répétitions: {reco_data.get('reps_recommandees')}")
                    print(f"   Séries: {reco_data.get('series_recommandees')}")
                    print(f"   Source: {reco_data.get('source')}")
                    return True
                else:
                    print(f"❌ Erreur lors de la récupération de recommandation: {reco_response.status_code}")
                    print(f"   Réponse: {reco_response.text}")
                    return False
            else:
                print("❌ Aucune machine trouvée")
                return False
        else:
            print(f"❌ Erreur lors de la récupération des machines: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test de recommandation: {e}")
        return False

def test_workout_history(token):
    """Teste la récupération de l'historique des séances"""
    print("\n📊 Test 3: Récupération de l'historique des séances...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/workouts/history/", headers=headers)

        if response.status_code == 200:
            history = response.json()
            print(f"✅ Historique récupéré: {len(history)} séances")

            if history:
                latest_workout = history[0]  # La plus récente
                print(f"   Dernière séance: {latest_workout.get('nom_seance')}")
                print(f"   Date: {latest_workout.get('date_seance')}")
                print(f"   Durée: {latest_workout.get('duree_minutes')} minutes")
                print(f"   Exercices: {len(latest_workout.get('exercices', []))}")

            return True
        else:
            print(f"❌ Erreur lors de la récupération de l'historique: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test d'historique: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 TEST COMPLET DU SYSTÈME AVEC AUTHENTIFICATION")
    print("=" * 60)

    # Test de connexion
    print("🔗 Test de connexion à l'API...")
    try:
        response = requests.get(f"{BASE_URL}/machines/")
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return

    # Créer l'utilisateur de test
    create_test_user()

    # Obtenir le token d'authentification
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir le token d'authentification")
        print("\n💡 Solutions possibles:")
        print("   1. Créer un utilisateur 'testuser' avec le mot de passe 'testpass123'")
        print("   2. Utiliser la commande: python manage.py createsuperuser")
        print("   3. Vérifier que le serveur Django est démarré sur le port 8000")
        return

    # Tests avec authentification
    success_count = 0
    total_tests = 3

    if test_workout_registration(token):
        success_count += 1

    if test_recommendation_retrieval(token):
        success_count += 1

    if test_workout_history(token):
        success_count += 1

    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print(f"✅ Tests réussis: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 Tous les tests sont passés avec succès !")
        print("\n💡 Le système est prêt pour l'utilisation :")
        print("   • L'enregistrement des séances fonctionne")
        print("   • Les recommandations sont calculées")
        print("   • L'historique est accessible")
        print("   • L'authentification est opérationnelle")
    else:
        print("⚠️ Certains tests ont échoué")
        print("   Vérifiez les logs ci-dessus pour plus de détails")

if __name__ == "__main__":
    main()