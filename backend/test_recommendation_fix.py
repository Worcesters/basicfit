#!/usr/bin/env python
"""
Test pour vérifier que les recommandations se mettent à jour après un entraînement
"""

import os
import django
import requests
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine, SeanceEntrainement
from apps.users.models import User
from apps.machines.models import Machine

def test_recommendation_update():
    print("TEST DE MISE A JOUR DES RECOMMANDATIONS")
    print("=" * 50)
    
    # 1. Vérifier l'état initial
    print("\n1. État initial des progressions:")
    progressions = ProgressionMachine.objects.all()[:3]
    
    for progression in progressions:
        print(f"   User: {progression.utilisateur.email} - {progression.machine.nom}")
        print(f"       Poids actuel: {progression.poids_actuel}kg")
        print(f"       Dernier 1RM: {progression.dernier_1rm}kg")
        print(f"       Nb séances: {progression.nombre_seances_machine}")
        
        # Calculer ce que devrait être la recommandation
        recommandation_calculee = progression.calculer_recommandation_professionnelle()
        print(f"       Recommandation calculée: {recommandation_calculee}kg")
        
        if abs(progression.poids_actuel - recommandation_calculee) > 0.1:
            print(f"       ATTENTION: DECALAGE DETECTE!")
    
    # 2. Simuler une nouvelle séance via l'API
    print("\n2. Test avec l'API de sauvegarde:")
    
    try:
        # Créer une séance de test
        user = User.objects.first()
        machine = Machine.objects.first()
        
        if user and machine:
            # Données de test pour une séance
            workout_data = {
                "nom": "Test Recommandation Fix",
                "duree": 45,
                "note_ressenti": 8,
                "exercices": [
                    {
                        "nom": machine.nom,
                        "series": 3,
                        "reps": 10,
                        "poids": 20.0
                    }
                ]
            }
            
            print(f"   Création d'une séance test avec {machine.nom} à 20kg")
            
            # Récupérer la progression avant
            try:
                progression_avant = ProgressionMachine.objects.get(
                    utilisateur=user, 
                    machine=machine
                )
                poids_avant = progression_avant.poids_actuel
                print(f"   Poids recommandé AVANT: {poids_avant}kg")
            except ProgressionMachine.DoesNotExist:
                poids_avant = None
                print("   Aucune progression existante")
            
            # Simuler l'appel API (sans faire d'appel HTTP réel)
            from apps.workouts.views import sauvegarder_seance_simple
            from django.test import RequestFactory
            from django.contrib.auth import get_user_model
            
            # Créer une requête factice
            factory = RequestFactory()
            request = factory.post('/api/workouts/sauvegarder/', 
                                 data=json.dumps(workout_data),
                                 content_type='application/json')
            request.user = user
            
            # Appeler la fonction directement
            try:
                response = sauvegarder_seance_simple(request)
                print(f"   Réponse API: {response.status_code}")
            except Exception as e:
                print(f"   Erreur API: {e}")
            
            # Vérifier la progression après
            try:
                progression_apres = ProgressionMachine.objects.get(
                    utilisateur=user, 
                    machine=machine
                )
                poids_apres = progression_apres.poids_actuel
                print(f"   Poids recommandé APRÈS: {poids_apres}kg")
                
                if poids_avant != poids_apres:
                    print(f"   ✅ RECOMMANDATION MISE À JOUR: {poids_avant}kg → {poids_apres}kg")
                else:
                    print(f"   ❌ Pas de changement: {poids_avant}kg → {poids_apres}kg")
                    
            except ProgressionMachine.DoesNotExist:
                print("   ❌ Aucune progression trouvée après la séance")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Vérifier que toutes les progressions sont à jour
    print("\n3. Vérification finale:")
    progressions_incorrectes = 0
    
    for progression in ProgressionMachine.objects.all():
        recommandation_calculee = progression.calculer_recommandation_professionnelle()
        
        if abs(progression.poids_actuel - recommandation_calculee) > 0.1:
            progressions_incorrectes += 1
            print(f"   ⚠️ Progression non synchronisée:")
            print(f"       {progression.utilisateur.email} - {progression.machine.nom}")
            print(f"       Stocké: {progression.poids_actuel}kg")
            print(f"       Calculé: {recommandation_calculee}kg")
    
    if progressions_incorrectes == 0:
        print("   ✅ Toutes les progressions sont synchronisées!")
    else:
        print(f"   ❌ {progressions_incorrectes} progressions non synchronisées")
        
        # Proposer un correctif automatique
        print("\n🔧 CORRECTIF AUTOMATIQUE:")
        for progression in ProgressionMachine.objects.all():
            recommandation_calculee = progression.calculer_recommandation_professionnelle()
            
            if abs(progression.poids_actuel - recommandation_calculee) > 0.1:
                ancien_poids = progression.poids_actuel
                progression.poids_actuel = recommandation_calculee
                progression.save()
                print(f"   ✅ {progression.machine.nom}: {ancien_poids}kg → {recommandation_calculee}kg")

if __name__ == "__main__":
    test_recommendation_update()