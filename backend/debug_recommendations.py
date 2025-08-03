#!/usr/bin/env python3
"""
Debug recommandations pour comprendre pourquoi ça ne fonctionne pas
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.workouts.models import ProgressionMachine, Machine, ModeEntrainement
from apps.workouts.simple_recommendation import SimpleRecommendationEngine

User = get_user_model()

def debug_recommendations():
    """Debug système de recommandations"""
    print("=== DEBUG RECOMMANDATIONS ===")
    
    # Test avec l'utilisateur test@railway.com
    test_users = ["test@railway.com", "test@example.com", "jeremy@example.com"]
    
    for email in test_users:
        print(f"\n--- Test pour {email} ---")
        
        try:
            user = User.objects.get(email=email)
            print(f"Utilisateur trouvé: {user.email} (ID: {user.id})")
            
            # Test avec Supine Press
            try:
                machine = Machine.objects.get(nom__icontains="Supine Press")
                print(f"Machine: {machine.nom} (ID: {machine.id})")
                
                # Créer le moteur de recommandation
                engine = SimpleRecommendationEngine(user, machine)
                
                # Vérifier les progressions
                progression = engine.get_user_progression()
                if progression:
                    print(f"  Progression trouvée: {progression.poids_actuel}kg x {progression.repetitions_actuelles}")
                    print(f"  Mode: {progression.mode_entrainement.nom}")
                else:
                    print("  Aucune progression trouvée")
                
                # Générer la recommandation
                rec = engine.calculate_recommendation()
                print(f"  Recommandation: {rec['poids_recommande']}kg x {rec['reps_recommandees']}")
                print(f"  Source: {rec['source']}")
                
            except Machine.DoesNotExist:
                print("  Machine Supine Press non trouvée")
                
        except User.DoesNotExist:
            print(f"  Utilisateur {email} non trouvé")
    
    # Créer compte test@railway.com avec progression si nécessaire
    print(f"\n=== CREATION COMPTE TEST@RAILWAY.COM ===")
    try:
        railway_user = User.objects.get(email="test@railway.com")
        print(f"Compte test@railway.com existe: {railway_user.id}")
    except User.DoesNotExist:
        print("Création du compte test@railway.com...")
        railway_user = User.objects.create_user(
            email="test@railway.com",
            password="testpass123",
            nom="TEST",
            prenom="Railway"
        )
        print(f"Compte créé: {railway_user.id}")
    
    # Créer progression pour test@railway.com
    try:
        machine = Machine.objects.get(nom__icontains="Supine Press")
        mode_force, _ = ModeEntrainement.objects.get_or_create(
            nom="Force",
            defaults={'description': 'Entraînement de force générale'}
        )
        
        progression, created = ProgressionMachine.objects.get_or_create(
            utilisateur=railway_user,
            machine=machine,
            mode_entrainement=mode_force,
            defaults={
                'poids_actuel': 60.0,
                'repetitions_actuelles': 8,
                'series_actuelles': 3,
                'niveau_maitrise': 85,
                'historique_charges': '[55.0, 57.5, 60.0]',
                'historique_performances': '[10, 9, 8]'
            }
        )
        
        if created:
            print(f"Progression créée pour test@railway.com: 60kg")
        else:
            progression.poids_actuel = 60.0
            progression.save()
            print(f"Progression mise à jour pour test@railway.com: 60kg")
            
        # Re-tester
        print(f"\n--- Re-test après création progression ---")
        engine = SimpleRecommendationEngine(railway_user, machine)
        rec = engine.calculate_recommendation()
        print(f"Nouvelle recommandation: {rec['poids_recommande']}kg")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    debug_recommendations()