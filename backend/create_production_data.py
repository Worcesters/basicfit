#!/usr/bin/env python
"""
Script pour créer des données de progression en production
"""
import os
import sys
import django
import requests

# Configuration pour Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')

try:
    django.setup()
    from django.contrib.auth import get_user_model
    from apps.workouts.models import ProgressionMachine, ModeEntrainement
    from apps.machines.models import Machine
    
    User = get_user_model()
    
    print("=== CREATION DONNEES PROGRESSION RAILWAY ===")
    
    # Trouver votre utilisateur réel (remplacez par votre email)
    try:
        user = User.objects.get(email='jeremy@example.com')  # Changez cet email
        print(f"Utilisateur trouvé: {user.email}")
    except User.DoesNotExist:
        print("Utilisateur non trouvé ! Créez d'abord un compte sur l'app.")
        sys.exit(1)
    
    # Récupérer la machine Supine Press
    try:
        machine = Machine.objects.get(nom='Supine Press')
        print(f"Machine trouvée: {machine.nom}")
    except Machine.DoesNotExist:
        print("Machine Supine Press non trouvée !")
        sys.exit(1)
    
    # Créer le mode Force
    mode_force, created = ModeEntrainement.objects.get_or_create(
        nom='Force',
        defaults={'description': 'Entraînement de force générale'}
    )
    print(f"Mode Force: {'créé' if created else 'existant'}")
    
    # Créer la progression avec 60kg
    progression, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        mode_entrainement=mode_force,
        defaults={
            'poids_actuel': 60.0,
            'repetitions_actuelles': 12,
            'series_actuelles': 3,
            'taux_reussite': 85.0,
            'nombre_seances_machine': 5
        }
    )
    
    if created:
        print(f"✅ Progression créée: {progression.poids_actuel}kg x {progression.repetitions_actuelles}")
    else:
        print(f"✅ Progression existante: {progression.poids_actuel}kg")
    
    # Test du système
    from apps.workouts.simple_recommendation import get_simple_recommendation_by_name
    result = get_simple_recommendation_by_name(user, 'Supine Press')
    
    if result['success']:
        data = result['data']
        print(f"🎯 RECOMMANDATION: {data['poids_recommande']}kg x {data['reps_recommandees']} ({data['source']})")
    else:
        print(f"❌ Erreur: {result['error']}")
    
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()