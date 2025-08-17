#!/usr/bin/env python3
"""
Test du système d'analyse intelligente et des recommandations basées sur les progressions
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.workouts.new_recommendation_system import ProgressionBasedRecommendationSystem
from apps.workouts.models import ProgressionMachine
from apps.machines.models import Machine
from apps.core.models import ModeEntrainement

User = get_user_model()

class IntelligentAnalysisTestCase(TestCase):
    """Tests pour l'analyse intelligente"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.user.nom = 'Test User'
        self.user.save()
        
        # Créer quelques machines de test
        self.machine1 = Machine.objects.create(
            nom='Développé couché',
            poids_minimum=20.0,
            poids_maximum=200.0,
            increment_poids=2.5
        )
        
        self.machine2 = Machine.objects.create(
            nom='Squat',
            poids_minimum=20.0,
            poids_maximum=300.0,
            increment_poids=2.5
        )
        
        # Créer un mode d'entraînement
        self.mode_force = ModeEntrainement.objects.create(
            nom='FORCE',
            description='Entraînement en force',
            series_recommandees=4,
            repetitions_min=1,
            repetitions_max=6,
            repos_entre_series=180
        )
        
        # Créer quelques progressions
        self.progression1 = ProgressionMachine.objects.create(
            utilisateur=self.user,
            machine=self.machine1,
            mode_entrainement=self.mode_force,
            poids_actuel=80.0,
            taux_reussite=85.0,
            nombre_seances_machine=10
        )
        
        self.progression2 = ProgressionMachine.objects.create(
            utilisateur=self.user,
            machine=self.machine2,
            mode_entrainement=self.mode_force,
            poids_actuel=100.0,
            taux_reussite=92.0,
            nombre_seances_machine=15
        )
        
        self.client = Client()
        
    def test_recommendation_system_with_progressions(self):
        """Test du système de recommandation avec progressions existantes"""
        system = ProgressionBasedRecommendationSystem()
        
        recommendations = system.get_recommendations_for_user(
            user=self.user,
            mode_entrainement='FORCE',
            nb_machines=2
        )
        
        self.assertEqual(len(recommendations), 2)
        
        # Vérifier que les recommandations contiennent les bonnes machines
        machine_names = [rec['machine_nom'] for rec in recommendations]
        self.assertIn('Développé couché', machine_names)
        self.assertIn('Squat', machine_names)
        
        # Vérifier les recommandations de poids
        for rec in recommendations:
            self.assertIn('poids_recommande', rec)
            self.assertIn('series_recommandees', rec)
            self.assertIn('repetitions_recommandees', rec)
            self.assertIn('notes', rec)
    
    def test_intelligent_recommendations_endpoint(self):
        """Test de l'endpoint des recommandations intelligentes"""
        # Se connecter
        self.client.force_login(self.user)
        
        url = reverse('get_intelligent_recommendations', kwargs={'mode_entrainement': 'FORCE'})
        response = self.client.get(url, {'nb_machines': 2})
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['mode_entrainement'], 'FORCE')
        
        # Vérifier la structure des recommandations
        rec = data['data'][0]
        required_fields = [
            'machine_id', 'machine_nom', 'poids_recommande',
            'series_recommandees', 'repetitions_recommandees',
            'repos_recommande', 'notes', 'progression_info'
        ]
        
        for field in required_fields:
            self.assertIn(field, rec)
    
    def test_user_progressions_endpoint(self):
        """Test de l'endpoint des progressions utilisateur"""
        # Se connecter
        self.client.force_login(self.user)
        
        url = reverse('get_user_progressions')
        response = self.client.get(url, {'mode_entrainement': 'FORCE'})
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 2)
        
        # Vérifier la structure des progressions
        prog = data['data'][0]
        required_fields = [
            'id', 'machine_id', 'machine_nom', 'mode_entrainement',
            'poids_actuel', 'taux_reussite', 'nombre_seances_machine'
        ]
        
        for field in required_fields:
            self.assertIn(field, prog)

def test_api_production():
    """Test des endpoints en production"""
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("Test de l'analyse intelligente en production...")
    
    # Test de connexion
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        # Test de ping
        response = requests.get(f"{BASE_URL}/users/android/ping/", timeout=10)
        print(f"OK Ping API: {response.status_code}")
        
        # Test des machines
        response = requests.get(f"{BASE_URL}/machines/", timeout=10)
        if response.status_code == 200:
            machines_data = response.json()
            print(f"OK Machines API: {len(machines_data.get('results', []))} machines disponibles")
        else:
            print(f"ERR Machines API: {response.status_code}")
            
        # Note: Les endpoints des recommandations nécessitent une authentification
        # donc on ne peut pas les tester facilement sans un utilisateur réel
        print("INFO: Les endpoints d'analyse intelligente necessitent une authentification")
        print("INFO: Utilisez l'application Android pour tester completement")
        
    except requests.exceptions.RequestException as e:
        print(f"ERR Erreur connexion API: {e}")

if __name__ == '__main__':
    print("Test du systeme d'analyse intelligente")
    print("=" * 50)
    
    # Test en mode Django
    print("\n1. Tests unitaires Django...")
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(IntelligentAnalysisTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Test API production
    print("\n2. Test API production...")
    test_api_production()
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("OK: Tous les tests sont passes!")
    else:
        print("ERR: Certains tests ont echoue")
        sys.exit(1)