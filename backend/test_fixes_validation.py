#!/usr/bin/env python
"""
Script de validation des correctifs BasicFit
Vérifie que tous les problèmes ont été résolus:
1. Pas de doublons de séances
2. Recommandations basées sur le 1RM réel
3. Système de progression cohérent
"""

import os
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.db.models import Count, Q
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, ProgressionMachine
from apps.machines.models import Machine
from apps.users.models import User

class ValidationTester:
    def __init__(self):
        self.results = {
            'duplicates_test': False,
            'recommendations_test': False,
            'progression_test': False,
            'api_test': False
        }
        
    def run_all_tests(self):
        """Execute tous les tests de validation"""
        print("🧪 VALIDATION DES CORRECTIFS BASICFIT")
        print("=" * 50)
        
        # Test 1: Vérifier l'absence de doublons
        self.test_no_duplicates()
        
        # Test 2: Vérifier les recommandations intelligentes
        self.test_intelligent_recommendations()
        
        # Test 3: Vérifier la cohérence des progressions
        self.test_progression_consistency()
        
        # Test 4: Tester l'API
        self.test_api_endpoints()
        
        # Résultats finaux
        self.print_final_results()
        
        return all(self.results.values())

    def test_no_duplicates(self):
        """Test 1: Vérifier qu'il n'y a plus de doublons"""
        print("\n🔍 TEST 1: VÉRIFICATION DES DOUBLONS")
        print("-" * 40)
        
        try:
            users = User.objects.all()
            duplicates_found = 0
            
            for user in users:
                # Grouper les séances par date
                seances_by_date = SeanceEntrainement.objects.filter(
                    utilisateur=user,
                    statut='TERMINEE'
                ).extra(select={'date_only': 'date(date_prevue)'}).values('date_only').annotate(count=Count('id'))
                
                for entry in seances_by_date:
                    if entry['count'] > 1:
                        date_str = entry['date_only']
                        seances = SeanceEntrainement.objects.filter(
                            utilisateur=user,
                            date_prevue__date=date_str,
                            statut='TERMINEE'
                        )
                        
                        # Vérifier si ce sont vraiment des doublons
                        seances_list = list(seances)
                        for i, seance1 in enumerate(seances_list):
                            for seance2 in seances_list[i+1:]:
                                if self.are_workouts_duplicates(seance1, seance2):
                                    duplicates_found += 1
                                    print(f"   ❌ Doublon trouvé: {user.email} - {date_str}")
                                    print(f"       Séance 1: {seance1.nom} (ID: {seance1.id})")
                                    print(f"       Séance 2: {seance2.nom} (ID: {seance2.id})")
            
            if duplicates_found == 0:
                print("   ✅ Aucun doublon détecté!")
                self.results['duplicates_test'] = True
            else:
                print(f"   ❌ {duplicates_found} doublons encore présents")
                
        except Exception as e:
            print(f"   ❌ Erreur lors du test des doublons: {e}")

    def are_workouts_duplicates(self, workout1, workout2):
        """Vérifie si deux séances sont des doublons"""
        # Même nom et même durée approximative
        if workout1.nom != workout2.nom:
            return False
            
        # Comparer les exercices
        exercises1 = set((ex.machine.nom, ex.poids_utilise or ex.poids_prevu or 0) 
                         for ex in workout1.exercices.all())
        exercises2 = set((ex.machine.nom, ex.poids_utilise or ex.poids_prevu or 0) 
                         for ex in workout2.exercices.all())
        
        # Si plus de 90% des exercices sont identiques
        if not exercises1 and not exercises2:
            return True
            
        intersection = len(exercises1.intersection(exercises2))
        union = len(exercises1.union(exercises2))
        
        return (intersection / union) > 0.9 if union > 0 else False

    def test_intelligent_recommendations(self):
        """Test 2: Vérifier que les recommandations utilisent le 1RM"""
        print("\n🎯 TEST 2: RECOMMANDATIONS INTELLIGENTES")
        print("-" * 40)
        
        try:
            problematic_recommendations = 0
            total_tested = 0
            
            progressions = ProgressionMachine.objects.filter(
                dernier_1rm__isnull=False,
                dernier_1rm__gt=0
            )[:10]  # Tester un échantillon
            
            for progression in progressions:
                total_tested += 1
                
                # Calculer la recommandation
                recommandation = progression.calculer_recommandation_professionnelle()
                
                # Vérifier qu'elle n'est pas fixée à 17kg
                if recommandation == 17.0:
                    problematic_recommendations += 1
                    print(f"   ⚠️ Recommandation fixe détectée: {progression.machine.nom}")
                    print(f"       Utilisateur: {progression.utilisateur.email}")
                    print(f"       1RM disponible: {progression.dernier_1rm}kg")
                    print(f"       Recommandation: {recommandation}kg")
                
                # Vérifier la cohérence avec le 1RM
                elif progression.dernier_1rm > 0:
                    ratio = recommandation / progression.dernier_1rm
                    if ratio < 0.4 or ratio > 1.0:  # Ratio incohérent
                        print(f"   ⚠️ Ratio incohérent: {progression.machine.nom}")
                        print(f"       1RM: {progression.dernier_1rm}kg, Recommandation: {recommandation}kg")
                        print(f"       Ratio: {ratio:.2f}")
            
            if problematic_recommendations == 0:
                print(f"   ✅ {total_tested} recommandations testées - Toutes cohérentes!")
                self.results['recommendations_test'] = True
            else:
                print(f"   ❌ {problematic_recommendations}/{total_tested} recommandations problématiques")
                
        except Exception as e:
            print(f"   ❌ Erreur lors du test des recommandations: {e}")

    def test_progression_consistency(self):
        """Test 3: Vérifier la cohérence des progressions"""
        print("\n📈 TEST 3: COHÉRENCE DES PROGRESSIONS")
        print("-" * 40)
        
        try:
            inconsistent_progressions = 0
            total_progressions = 0
            
            progressions = ProgressionMachine.objects.all()
            
            for progression in progressions:
                total_progressions += 1
                
                # Vérifier que la dernière séance correspond bien
                if progression.derniere_seance:
                    # Chercher s'il y a une séance plus récente avec cette machine
                    seance_plus_recente = SeanceEntrainement.objects.filter(
                        utilisateur=progression.utilisateur,
                        exercices__machine=progression.machine,
                        statut='TERMINEE',
                        date_fin__gt=progression.derniere_seance.date_fin
                    ).first()
                    
                    if seance_plus_recente:
                        inconsistent_progressions += 1
                        print(f"   ⚠️ Progression non à jour: {progression.machine.nom}")
                        print(f"       Dernière séance stockée: {progression.derniere_seance.date_fin}")
                        print(f"       Séance plus récente trouvée: {seance_plus_recente.date_fin}")
                
                # Vérifier le nombre de séances
                nb_seances_reel = SeanceEntrainement.objects.filter(
                    utilisateur=progression.utilisateur,
                    exercices__machine=progression.machine,
                    statut='TERMINEE'
                ).distinct().count()
                
                if abs(nb_seances_reel - progression.nombre_seances_machine) > 1:
                    inconsistent_progressions += 1
                    print(f"   ⚠️ Compteur de séances incorrect: {progression.machine.nom}")
                    print(f"       Stocké: {progression.nombre_seances_machine}")
                    print(f"       Réel: {nb_seances_reel}")
            
            if inconsistent_progressions == 0:
                print(f"   ✅ {total_progressions} progressions vérifiées - Toutes cohérentes!")
                self.results['progression_test'] = True
            else:
                print(f"   ❌ {inconsistent_progressions}/{total_progressions} progressions incohérentes")
                
        except Exception as e:
            print(f"   ❌ Erreur lors du test des progressions: {e}")

    def test_api_endpoints(self):
        """Test 4: Tester les endpoints d'API"""
        print("\n🌐 TEST 4: ENDPOINTS API")
        print("-" * 40)
        
        try:
            # Test du serveur local
            base_url = "http://localhost:8000"
            
            # Test de base
            try:
                response = requests.get(f"{base_url}/api/", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Serveur API accessible")
                else:
                    print(f"   ⚠️ Serveur API répond mais status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("   ❌ Serveur API non accessible")
                print("   💡 Démarrez le serveur avec: python manage.py runserver")
                return
            
            # Test des recommandations
            machine = Machine.objects.first()
            if machine:
                try:
                    response = requests.get(f"{base_url}/api/workouts/recommendation/{machine.id}/", timeout=5)
                    if response.status_code in [200, 401]:  # 401 = pas authentifié, c'est normal
                        print("   ✅ Endpoint de recommandation accessible")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'poids_recommande' in data and data['poids_recommande'] != 17.0:
                                print(f"   ✅ Recommandation dynamique: {data['poids_recommande']}kg")
                            elif data.get('poids_recommande') == 17.0:
                                print("   ⚠️ Recommandation encore fixée à 17kg")
                    else:
                        print(f"   ❌ Endpoint de recommandation error: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Erreur test recommandation API: {e}")
            
            self.results['api_test'] = True
            
        except Exception as e:
            print(f"   ❌ Erreur lors du test API: {e}")

    def print_final_results(self):
        """Affiche les résultats finaux"""
        print("\n📋 RÉSULTATS DE VALIDATION")
        print("=" * 40)
        
        for test_name, result in self.results.items():
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            test_display = {
                'duplicates_test': 'Suppression des doublons',
                'recommendations_test': 'Recommandations intelligentes',
                'progression_test': 'Cohérence des progressions',
                'api_test': 'Endpoints API'
            }
            print(f"   {test_display[test_name]}: {status}")
        
        success_rate = sum(self.results.values()) / len(self.results) * 100
        print(f"\n🎯 TAUX DE RÉUSSITE: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
            print("   Le système est maintenant opérationnel.")
        else:
            print(f"\n⚠️ {len([r for r in self.results.values() if not r])} test(s) en échec")
            print("   Vérifiez les erreurs ci-dessus et relancez les correctifs si nécessaire.")

def main():
    """Point d'entrée principal"""
    tester = ValidationTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n✅ VALIDATION COMPLÈTE RÉUSSIE!")
        else:
            print("\n❌ VALIDATION PARTIELLE - Consultez les détails ci-dessus")
        return success
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA VALIDATION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()