#!/usr/bin/env python3
"""
Script de test pour vérifier la gestion des exercices cardio
"""
import requests
import json
from datetime import datetime, timezone

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/users/android/login/"
SAUVEGARDER_URL = f"{BASE_URL}/workouts/sauvegarder/"

def test_login():
    """Test de connexion pour obtenir un token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }

    print("🔐 Test de connexion...")
    response = requests.post(LOGIN_URL, json=login_data)

    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('token'):
            print("✅ Connexion réussie!")
            return data['token']
        else:
            print(f"❌ Échec de connexion: {data}")
            return None
    else:
        print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
        return None

def test_cardio_exercises(token):
    """Test de sauvegarde avec exercices cardio"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Données de test avec exercices cardio
    seance_data = {
        "nom": "Séance cardio test",
        "duree": 30,
        "note_ressenti": 8,
        "commentaire": "Test exercices cardio",
        "exercices": [
            {
                "nom": "Tapis de course",
                "series": 1,
                "reps": 20,  # 20 minutes
                "poids": 0.0,
                "type_exercice": "DUREE"
            },
            {
                "nom": "Vélo elliptique",
                "series": 1,
                "reps": 15,  # 15 minutes
                "poids": 0.0,
                "type_exercice": "DUREE"
            },
            {
                "nom": "Développé couché",  # Exercice musculation pour comparaison
                "series": 3,
                "reps": 10,
                "poids": 80.0,
                "type_exercice": "REPETITIONS"
            }
        ]
    }

    print(f"\n🏃 Test sauvegarde séance avec cardio...")
    print(f"URL: {SAUVEGARDER_URL}")
    print(f"Données: {json.dumps(seance_data, indent=2)}")

    response = requests.post(SAUVEGARDER_URL, json=seance_data, headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✅ Séance cardio sauvegardée avec succès!")
        print(f"   ID: {data.get('id')}")
        print(f"   Nom: {data.get('nom')}")
        print(f"   Statut: {data.get('statut')}")
        print(f"   Message: {data.get('message', 'N/A')}")

        # Vérifier les détails dans la base de données
        print("\n📊 Vérification des exercices sauvegardés...")
        check_exercises_in_db(data.get('id'))

    else:
        print(f"❌ Erreur: {response.text}")
        try:
            error_data = response.json()
            print(f"   Détails: {error_data}")
        except:
            pass

def check_exercises_in_db(seance_id):
    """Vérifier les exercices dans la base de données"""
    try:
        from django.db import connection
        from django.conf import settings
        import os
        import sys

        # Ajouter le chemin du projet Django
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.basicfit_project.settings.development')

        import django
        django.setup()

        from apps.workouts.models import ExerciceSeance
        from apps.machines.models import Machine

        # Récupérer les exercices de la séance
        exercices = ExerciceSeance.objects.filter(seance_id=seance_id).order_by('ordre_dans_seance')

        print(f"   Exercices trouvés: {exercices.count()}")

        for i, exercice in enumerate(exercices, 1):
            machine = exercice.machine
            is_cardio = machine.categorie.nom == 'CARDIO' if machine.categorie else False

            print(f"   {i}. {machine.nom}")
            print(f"      Catégorie: {machine.categorie.nom if machine.categorie else 'N/A'}")
            print(f"      Type exercice: {'Cardio' if is_cardio else 'Musculation'}")
            print(f"      Séries: {exercice.series_prevues}")
            print(f"      Répétitions: {exercice.repetitions_prevues}")
            print(f"      Durée prévue: {exercice.duree_prevue}s" if exercice.duree_prevue else "      Durée prévue: N/A")
            print(f"      Poids: {exercice.poids_prevu}kg")
            print(f"      Statut: {exercice.statut}")
            print()

    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification: {e}")

def main():
    """Fonction principale"""
    print("🧪 Test de gestion des exercices cardio")
    print("=" * 50)

    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de se connecter, arrêt du test")
        return

    # Test des exercices cardio
    test_cardio_exercises(token)

    print("\n✅ Test terminé!")

if __name__ == "__main__":
    main()