#!/usr/bin/env python
"""
Script de nettoyage des doublons et correction du système de recommandation BasicFit
Ce script résout les problèmes de:
1. Séances d'entraînement dupliquées
2. Recommandations fixées à 17kg
3. Progressions incohérentes
"""

import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.db.models import Count, Max, Min, Q
from django.utils import timezone
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
from apps.machines.models import Machine
from apps.users.models import User
from apps.core.models import ModeEntrainement

class DatabaseFixer:
    def __init__(self):
        self.stats = {
            'duplicates_removed': 0,
            'progressions_fixed': 0,
            'recommendations_updated': 0,
            'metrics_recalculated': 0
        }
        
    def run_all_fixes(self):
        """Execute tous les correctifs dans l'ordre approprié"""
        print("🔧 DÉMARRAGE DU CORRECTIF COMPLET BASICFIT")
        print("=" * 60)
        
        # 1. Nettoyer les doublons
        self.remove_duplicate_workouts()
        
        # 2. Recalculer les métriques
        self.recalculate_exercise_metrics()
        
        # 3. Corriger les progressions
        self.fix_progression_data()
        
        # 4. Mettre à jour les recommandations
        self.update_recommendations()
        
        # 5. Statistiques finales
        self.print_final_stats()
        
        print("\n✅ CORRECTIF TERMINÉ AVEC SUCCÈS!")
        return True

    def remove_duplicate_workouts(self):
        """Supprime les séances d'entraînement dupliquées"""
        print("\n🧹 NETTOYAGE DES DOUBLONS DE SÉANCES...")
        
        users = User.objects.all()
        
        for user in users:
            print(f"   👤 Utilisateur: {user.email}")
            
            # Grouper les séances par date et nom
            seances_by_date = {}
            seances = SeanceEntrainement.objects.filter(
                utilisateur=user,
                statut='TERMINEE'
            ).order_by('date_debut')
            
            for seance in seances:
                date_key = seance.date_prevue.date() if seance.date_prevue else seance.date_debut.date()
                if date_key not in seances_by_date:
                    seances_by_date[date_key] = []
                seances_by_date[date_key].append(seance)
            
            # Identifier et supprimer les doublons
            for date_key, seances_list in seances_by_date.items():
                if len(seances_list) > 1:
                    # Garder la séance avec le plus d'exercices ou la plus récente
                    best_seance = max(seances_list, key=lambda s: (
                        s.exercices.count(),
                        s.date_debut or s.date_prevue
                    ))
                    
                    duplicates = [s for s in seances_list if s.id != best_seance.id]
                    
                    # Vérifier si ce sont vraiment des doublons (même contenu)
                    for duplicate in duplicates:
                        if self.are_workouts_similar(best_seance, duplicate):
                            print(f"      🗑️ Suppression doublon: {duplicate.nom} ({duplicate.id})")
                            duplicate.delete()
                            self.stats['duplicates_removed'] += 1

    def are_workouts_similar(self, workout1, workout2):
        """Vérifie si deux séances sont similaires (probablement des doublons)"""
        # Comparer le nom et la durée
        if workout1.nom != workout2.nom:
            return False
            
        # Comparer les exercices
        exercises1 = set((ex.machine.nom, ex.poids_utilise or ex.poids_prevu) 
                         for ex in workout1.exercices.all())
        exercises2 = set((ex.machine.nom, ex.poids_utilise or ex.poids_prevu) 
                         for ex in workout2.exercices.all())
        
        # Si plus de 80% des exercices sont identiques, c'est un doublon
        if len(exercises1) == 0 and len(exercises2) == 0:
            return True
            
        intersection = len(exercises1.intersection(exercises2))
        union = len(exercises1.union(exercises2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.8

    def recalculate_exercise_metrics(self):
        """Recalcule les métriques d'exercices (1RM, volume, etc.)"""
        print("\n📊 RECALCUL DES MÉTRIQUES D'EXERCICES...")
        
        exercises = ExerciceSeance.objects.filter(
            poids_utilise__isnull=False,
            repetitions_realisees__gt=0
        )
        
        for exercise in exercises:
            old_1rm = exercise.charge_maximale_theorique
            exercise.calculer_metriques()
            exercise.save()
            
            if old_1rm != exercise.charge_maximale_theorique:
                self.stats['metrics_recalculated'] += 1
                
        print(f"   ✅ {self.stats['metrics_recalculated']} métriques recalculées")

    def fix_progression_data(self):
        """Corrige les données de progression incohérentes"""
        print("\n🔄 CORRECTION DES PROGRESSIONS...")
        
        progressions = ProgressionMachine.objects.all()
        
        for progression in progressions:
            # Trouver la dernière séance réelle avec cette machine
            derniere_seance = SeanceEntrainement.objects.filter(
                utilisateur=progression.utilisateur,
                exercices__machine=progression.machine,
                statut='TERMINEE'
            ).order_by('-date_fin').first()
            
            if derniere_seance:
                # Mettre à jour avec les vraies données
                dernier_exercice = derniere_seance.exercices.filter(
                    machine=progression.machine
                ).first()
                
                if dernier_exercice:
                    old_weight = progression.poids_actuel
                    old_1rm = progression.dernier_1rm
                    
                    progression.poids_actuel = dernier_exercice.poids_utilise or dernier_exercice.poids_prevu
                    progression.dernier_1rm = dernier_exercice.charge_maximale_theorique
                    progression.derniere_seance = derniere_seance
                    
                    # Compter le nombre réel de séances
                    nb_seances = SeanceEntrainement.objects.filter(
                        utilisateur=progression.utilisateur,
                        exercices__machine=progression.machine,
                        statut='TERMINEE'
                    ).distinct().count()
                    
                    progression.nombre_seances_machine = nb_seances
                    progression.save()
                    
                    if old_weight != progression.poids_actuel or old_1rm != progression.dernier_1rm:
                        print(f"   🔧 {progression.utilisateur.email} - {progression.machine.nom}")
                        print(f"      Poids: {old_weight}kg → {progression.poids_actuel}kg")
                        print(f"      1RM: {old_1rm} → {progression.dernier_1rm}")
                        self.stats['progressions_fixed'] += 1
            
            # Supprimer les progressions sans données réelles
            elif progression.nombre_seances_machine == 0:
                print(f"   🗑️ Suppression progression vide: {progression.machine.nom}")
                progression.delete()

    def update_recommendations(self):
        """Met à jour toutes les recommandations avec la nouvelle logique"""
        print("\n🎯 MISE À JOUR DES RECOMMANDATIONS...")
        
        # Mettre à jour toutes les progressions existantes
        progressions = ProgressionMachine.objects.all()
        
        for progression in progressions:
            try:
                old_recommendation = progression.poids_actuel
                new_recommendation = progression.calculer_recommandation_professionnelle()
                
                if abs(old_recommendation - new_recommendation) > 0.1:  # Changement significatif
                    print(f"   🎯 {progression.utilisateur.email} - {progression.machine.nom}")
                    print(f"      Recommandation: {old_recommendation}kg → {new_recommendation}kg")
                    print(f"      1RM actuel: {progression.dernier_1rm}kg")
                    print(f"      Nombre séances: {progression.nombre_seances_machine}")
                    
                    progression.poids_actuel = new_recommendation
                    progression.save()
                    self.stats['recommendations_updated'] += 1
                    
            except Exception as e:
                print(f"   ❌ Erreur recommandation {progression.machine.nom}: {e}")

    def create_missing_progressions(self):
        """Crée les progressions manquantes pour les utilisateurs actifs"""
        print("\n➕ CRÉATION DES PROGRESSIONS MANQUANTES...")
        
        users = User.objects.filter(is_active=True)
        machines = Machine.objects.filter(est_disponible=True)
        mode_defaut = ModeEntrainement.objects.filter(nom='PRISE_MASSE').first()
        
        if not mode_defaut:
            mode_defaut = ModeEntrainement.objects.first()
            
        for user in users:
            # Trouver les machines que l'utilisateur a déjà utilisées mais n'a pas de progression
            machines_utilisees = Machine.objects.filter(
                exercices__seance__utilisateur=user,
                exercices__seance__statut='TERMINEE'
            ).distinct()
            
            for machine in machines_utilisees:
                if not ProgressionMachine.objects.filter(utilisateur=user, machine=machine).exists():
                    # Créer une progression basée sur la dernière séance
                    derniere_seance = SeanceEntrainement.objects.filter(
                        utilisateur=user,
                        exercices__machine=machine,
                        statut='TERMINEE'
                    ).order_by('-date_fin').first()
                    
                    if derniere_seance:
                        dernier_exercice = derniere_seance.exercices.filter(machine=machine).first()
                        if dernier_exercice:
                            ProgressionMachine.objects.create(
                                utilisateur=user,
                                machine=machine,
                                mode_entrainement=mode_defaut,
                                poids_actuel=dernier_exercice.poids_utilise or dernier_exercice.poids_prevu or machine.poids_minimum,
                                series_actuelles=dernier_exercice.nombre_series or 3,
                                repetitions_actuelles=dernier_exercice.repetitions_realisees or 10,
                                derniere_seance=derniere_seance,
                                dernier_1rm=dernier_exercice.charge_maximale_theorique,
                                nombre_seances_machine=1
                            )
                            print(f"   ➕ Progression créée: {user.email} - {machine.nom}")

    def print_final_stats(self):
        """Affiche les statistiques finales"""
        print("\n📈 STATISTIQUES FINALES:")
        print("=" * 40)
        print(f"   🗑️ Doublons supprimés: {self.stats['duplicates_removed']}")
        print(f"   📊 Métriques recalculées: {self.stats['metrics_recalculated']}")
        print(f"   🔧 Progressions corrigées: {self.stats['progressions_fixed']}")
        print(f"   🎯 Recommandations mises à jour: {self.stats['recommendations_updated']}")
        
        # Statistiques sur l'état actuel
        total_users = User.objects.filter(is_active=True).count()
        total_workouts = SeanceEntrainement.objects.filter(statut='TERMINEE').count()
        total_progressions = ProgressionMachine.objects.count()
        
        print(f"\n📊 ÉTAT ACTUEL:")
        print(f"   👥 Utilisateurs actifs: {total_users}")
        print(f"   🏋️ Séances terminées: {total_workouts}")
        print(f"   📈 Progressions: {total_progressions}")

def main():
    """Point d'entrée principal"""
    fixer = DatabaseFixer()
    
    try:
        success = fixer.run_all_fixes()
        if success:
            print("\n🎉 TOUS LES CORRECTIFS ONT ÉTÉ APPLIQUÉS AVEC SUCCÈS!")
            print("\n📋 ACTIONS RECOMMANDÉES:")
            print("   1. Testez l'API de recommandation: python test_api_recommendation.py")
            print("   2. Compilez et testez l'app Android")
            print("   3. Vérifiez que les doublons n'apparaissent plus")
            print("   4. Confirmez que les recommandations utilisent bien le 1RM")
        return success
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU CORRECTIF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()