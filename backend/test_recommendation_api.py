#!/usr/bin/env python
"""
Script pour tester l'API de recommandation
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine
from apps.machines.models import Machine
from apps.users.models import User
from django.utils import timezone

def test_recommendation_api():
    """
    Teste l'API de recommandation
    """
    print("🧪 Test de l'API de recommandation...")

    # URL de base (ajustez selon votre configuration)
    base_url = "http://localhost:8000"

    # Créer un utilisateur de test si nécessaire
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            'nom': "Test",
            'prenom': "User",
            'objectif_sportif': "PRISE_MASSE"
        }
    )

    if created:
        print(f"✅ Utilisateur de test créé: {user.email}")
    else:
        print(f"✅ Utilisateur de test existant: {user.email}")

    # Récupérer quelques machines
    machines = Machine.objects.all()[:5]

    print(f"\n📊 Test avec {machines.count()} machines:")

    for machine in machines:
        print(f"\n--- Machine: {machine.nom} ---")

        # Créer une progression de test si elle n'existe pas
        progression, created = ProgressionMachine.objects.get_or_create(
            utilisateur=user,
            machine=machine,
            defaults={
                'poids_actuel': 20.0,
                'taux_reussite': 85.0,
                'nombre_seances_machine': 5,
                'progression_poids_total': 10.0
            }
        )

        if created:
            print(f"✅ Progression créée pour {machine.nom}")
        else:
            print(f"✅ Progression existante pour {machine.nom}")
            print(f"   Poids actuel: {progression.poids_actuel}kg")
            print(f"   Taux de réussite: {progression.taux_reussite}%")
            print(f"   Nombre de séances: {progression.nombre_seances_machine}")

        # Tester la recommandation intelligente
        recommandation_intelligente = progression.calculer_recommandation_intelligente()
        print(f"   Recommandation intelligente: {recommandation_intelligente}kg")

        # Tester l'évaluation de progression
        peut_progresser = progression.evaluer_progression_historique()
        print(f"   Peut progresser: {peut_progresser}")

        # Tester la détection de stagnation
        stagnation = progression.detecter_stagnation()
        print(f"   Détecte stagnation: {stagnation}")

def test_api_endpoints():
    """
    Teste les endpoints de l'API
    """
    print("\n🌐 Test des endpoints API...")

    base_url = "http://localhost:8000"

    # Test de l'endpoint de recommandation par nom
    test_machine_name = "Développé couché"

    try:
        response = requests.get(f"{base_url}/workouts/recommendation/{test_machine_name}/")
        print(f"📡 GET /workouts/recommendation/{test_machine_name}/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Poids recommandé: {data.get('poids_recommande')}kg")
            print(f"   Peut progresser: {data.get('peut_progresser')}")
            print(f"   Source: {data.get('source')}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Erreur de connexion: {e}")

def simulate_progression():
    """
    Simule une progression pour tester
    """
    print("\n📈 Simulation de progression...")

    # Récupérer un utilisateur et une machine
    user = User.objects.first()
    if not user:
        print("❌ Aucun utilisateur trouvé")
        return

    machine = Machine.objects.first()
    if not machine:
        print("❌ Aucune machine trouvée")
        return

    print(f"👤 Utilisateur: {user.nom_complet}")
    print(f"🏋️ Machine: {machine.nom}")

    # Créer ou récupérer la progression
    progression, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        defaults={
            'poids_actuel': 20.0,
            'taux_reussite': 90.0,
            'nombre_seances_machine': 3,
            'progression_poids_total': 0.0
        }
    )

    print(f"📊 État initial:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")
    print(f"   Nombre de séances: {progression.nombre_seances_machine}")

    # Simuler une progression
    if progression.evaluer_progression_historique():
        success, ancien_poids, nouveau_poids = progression.progresser_poids()
        if success:
            print(f"✅ Progression réussie: {ancien_poids}kg → {nouveau_poids}kg")
        else:
            print(f"❌ Progression échouée")
    else:
        print(f"ℹ️ Pas de progression possible (taux: {progression.taux_reussite}%)")

if __name__ == "__main__":
    print("🚀 Test de l'API de recommandation")
    print("=" * 50)

    # Test des modèles
    test_recommendation_api()

    # Test des endpoints API
    test_api_endpoints()

    # Simulation de progression
    simulate_progression()

    print("\n✅ Tests terminés")