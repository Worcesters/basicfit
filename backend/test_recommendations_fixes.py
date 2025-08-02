#!/usr/bin/env python
"""
Script de test pour vérifier les corrections du système de recommandations
"""
import os
import django
import sys

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.workouts.simple_recommendation import get_simple_recommendation
from apps.machines.models import Machine
from apps.workouts.models import ProgressionMachine, ModeEntrainement

User = get_user_model()

def test_no_workout_data():
    """Test avec utilisateur sans données d'entraînement"""
    print("=== TEST 1: Utilisateur sans données ===")
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        email='test@basicfit.com',
        defaults={
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Supprimer toutes les progressions existantes pour ce test
    ProgressionMachine.objects.filter(utilisateur=user).delete()
    
    # Tester avec une machine aléatoire
    machine = Machine.objects.first()
    if machine:
        result = get_simple_recommendation(user, machine.id)
        
        print(f"Machine: {machine.nom}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            data = result['data']
            print(f"Message: {data.get('message', data.get('notes', 'N/A'))}")
            print(f"Peut progresser: {data.get('peut_progresser', 'N/A')}")
            print(f"Objectif: {data.get('objectif', 'N/A')}")
            print(f"Poids recommandé: {data.get('poids_recommande', 'N/A')}")
            print(f"Séries recommandées: {data.get('series_recommandees', 'N/A')}")
        else:
            print(f"Erreur: {result.get('error', 'Unknown error')}")
    else:
        print("Aucune machine trouvée dans la base de données")

def test_with_progression_data():
    """Test avec utilisateur ayant des données de progression"""
    print("\n=== TEST 2: Utilisateur avec progression ===")
    
    user = User.objects.filter(email='test@basicfit.com').first()
    if not user:
        print("Utilisateur de test non trouvé")
        return
    
    # Créer une progression avec 6 séries (pour tester la limite)
    machine = Machine.objects.first()
    if machine:
        mode_force, _ = ModeEntrainement.objects.get_or_create(
            nom="Force",
            defaults={'description': 'Entraînement de force générale'}
        )
        
        progression, created = ProgressionMachine.objects.get_or_create(
            utilisateur=user,
            machine=machine,
            mode_entrainement=mode_force,
            defaults={
                'poids_actuel': 25.0,
                'series_actuelles': 6,  # Valeur problématique
                'repetitions_actuelles': 10,
                'nombre_seances_machine': 1,
                'dernier_1rm': 30.0,
                'taux_reussite': 80.0
            }
        )
        
        if not created:
            # Mettre à jour avec les valeurs de test
            progression.poids_actuel = 25.0
            progression.series_actuelles = 6  # Valeur problématique
            progression.repetitions_actuelles = 10
            progression.save()
        
        result = get_simple_recommendation(user, machine.id)
        
        print(f"Machine: {machine.nom}")
        print(f"Progression existante - Séries stockées: {progression.series_actuelles}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            data = result['data']
            print(f"Source: {data.get('source', 'N/A')}")
            print(f"Poids recommandé: {data.get('poids_recommande', 'N/A')}")
            print(f"Séries recommandées: {data.get('series_recommandees', 'N/A')} (devrait être entre 3-4)")
            print(f"Répétitions recommandées: {data.get('reps_recommandees', 'N/A')}")
            
            # Vérifier que les séries sont bien limitées
            series_rec = data.get('series_recommandees')
            if series_rec and 3 <= series_rec <= 4:
                print("✅ CORRECTION RÉUSSIE: Séries limitées entre 3-4")
            else:
                print(f"❌ PROBLÈME: Séries non limitées: {series_rec}")
        else:
            print(f"Erreur: {result.get('error', 'Unknown error')}")

def test_recommendation_endpoints():
    """Test des endpoints de recommandation"""
    print("\n=== TEST 3: Test format de réponse 'Aucune recommandation' ===")
    
    # Tester le format de réponse pour aucune donnée
    user = User.objects.filter(email='test@basicfit.com').first()
    if user:
        # Supprimer toutes les progressions et séances
        from apps.workouts.models import SeanceEntrainement
        ProgressionMachine.objects.filter(utilisateur=user).delete()
        SeanceEntrainement.objects.filter(utilisateur=user).delete()
        
        machine = Machine.objects.first()
        if machine:
            result = get_simple_recommendation(user, machine.id)
            
            if result['success']:
                data = result['data']
                message = data.get('message', data.get('notes', ''))
                if 'Aucune recommandation' in message:
                    print("✅ MESSAGE CORRECT: 'Aucune recommandation pour cette machine'")
                    print(f"Message complet: {message}")
                else:
                    print(f"❌ MESSAGE INCORRECT: {message}")
            else:
                print("Pas de succès, mais cela peut être normal pour ce test")

if __name__ == "__main__":
    print("🔧 Test des corrections du système de recommandations")
    print("=" * 60)
    
    try:
        test_no_workout_data()
        test_with_progression_data()
        test_recommendation_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ Tests terminés! Vérifiez les résultats ci-dessus.")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()