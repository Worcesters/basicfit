"""
Système de recommandation simplifié et robuste
Récupère les progressions et calcule les recommandations appropriées
"""
import logging
from typing import Dict, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import ProgressionMachine, SeanceEntrainement, ExerciceSeance, ModeEntrainement
from apps.machines.models import Machine

logger = logging.getLogger(__name__)
User = get_user_model()

class SimpleRecommendationEngine:
    """Moteur de recommandation simplifié"""
    
    def __init__(self, user, machine):
        self.user = user
        self.machine = machine
        
    def get_user_progression(self) -> Optional[ProgressionMachine]:
        """Récupère la progression de l'utilisateur pour cette machine"""
        try:
            # Récupérer le mode Force par défaut
            mode_force, _ = ModeEntrainement.objects.get_or_create(
                nom="Force",
                defaults={'description': 'Entraînement de force générale'}
            )
            
            progression = ProgressionMachine.objects.filter(
                utilisateur=self.user,
                machine=self.machine,
                mode_entrainement=mode_force
            ).first()
            
            if progression:
                logger.info(f"Progression trouvée: {progression.poids_actuel}kg x {progression.repetitions_actuelles}")
                return progression
            else:
                logger.info(f"Aucune progression trouvée pour {self.machine.nom}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur récupération progression: {e}")
            return None
    
    def get_recent_workouts(self) -> list:
        """Récupère les dernières séances pour cette machine"""
        try:
            # Dernières séances des 30 derniers jours
            since = timezone.now() - timedelta(days=30)
            
            recent_exercises = ExerciceSeance.objects.filter(
                seance__utilisateur=self.user,
                machine=self.machine,
                seance__statut='TERMINEE',
                seance__date_debut__gte=since
            ).order_by('-seance__date_debut')[:5]
            
            workouts = []
            for exercise in recent_exercises:
                if exercise.series.exists():
                    last_set = exercise.series.last()
                    workouts.append({
                        'date': exercise.seance.date_debut,
                        'poids': last_set.poids_utilise,
                        'reps': last_set.repetitions_realisees,
                        'sets': exercise.nombre_series
                    })
            
            logger.info(f"Trouvé {len(workouts)} séances récentes")
            return workouts
            
        except Exception as e:
            logger.error(f"Erreur récupération séances: {e}")
            return []
    
    def calculate_recommendation(self) -> Dict:
        """Calcule la recommandation basée sur la progression"""
        try:
            # 1. Récupérer la progression actuelle
            progression = self.get_user_progression()
            recent_workouts = self.get_recent_workouts()
            
            # 2. Déterminer le poids de base
            if progression and progression.poids_actuel > 0:
                base_weight = progression.poids_actuel
                base_reps = progression.repetitions_actuelles
                base_sets = progression.series_actuelles
                source = "progression"
                logger.info(f"Base sur progression: {base_weight}kg")
            elif recent_workouts:
                # Utiliser la dernière séance
                last_workout = recent_workouts[0]
                base_weight = last_workout['poids']
                base_reps = last_workout['reps']
                base_sets = last_workout['sets']
                source = "dernière séance"
                logger.info(f"Base sur dernière séance: {base_weight}kg")
            else:
                # Valeurs par défaut pour débutant
                base_weight = self._get_default_weight()
                base_reps = 10
                base_sets = 3
                source = "défaut débutant"
                logger.info(f"Base par défaut: {base_weight}kg")
            
            # 3. Calculer la progression
            recommended_weight = self._calculate_progression(base_weight, progression, recent_workouts)
            recommended_reps = min(12, max(8, base_reps))  # Entre 8 et 12 reps
            recommended_sets = min(4, max(3, base_sets))   # Entre 3 et 4 sets
            
            # 4. Retourner la recommandation
            return {
                'machine_id': self.machine.id,
                'machine_nom': self.machine.nom,
                'poids_recommande': recommended_weight,
                'series_recommandees': recommended_sets,
                'reps_recommandees': recommended_reps,
                'repos_recommande': 90,
                'objectif': 'PROGRESSION',
                'source': source,
                'notes': f"Basé sur {source}",
                'peut_progresser': True
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul recommandation: {e}")
            return self._get_fallback_recommendation()
    
    def _calculate_progression(self, base_weight: float, progression: ProgressionMachine, recent_workouts: list) -> float:
        """Calcule la progression du poids"""
        try:
            # Si pas de progression récente, maintenir le poids
            if not recent_workouts:
                return base_weight
            
            # Analyser les performances récentes
            success_rate = self._calculate_success_rate(recent_workouts)
            
            if success_rate >= 0.8:  # 80% de réussite
                # Progression : +2.5kg ou +5% 
                increment = max(2.5, base_weight * 0.05)
                new_weight = base_weight + increment
                logger.info(f"Progression recommandée: {base_weight}kg → {new_weight}kg (succès: {success_rate*100:.0f}%)")
                return new_weight
            elif success_rate >= 0.6:  # 60-80% de réussite
                # Maintenir le poids
                logger.info(f"Maintien du poids: {base_weight}kg (succès: {success_rate*100:.0f}%)")
                return base_weight
            else:
                # Réduire le poids de 5-10%
                reduction = base_weight * 0.1
                new_weight = max(base_weight - reduction, base_weight * 0.5)  # Minimum 50% du poids original
                logger.info(f"Réduction recommandée: {base_weight}kg → {new_weight}kg (succès: {success_rate*100:.0f}%)")
                return new_weight
                
        except Exception as e:
            logger.error(f"Erreur calcul progression: {e}")
            return base_weight
    
    def _calculate_success_rate(self, workouts: list) -> float:
        """Calcule le taux de réussite basé sur les séances récentes"""
        if not workouts:
            return 0.5
        
        # Analyser si l'utilisateur a pu maintenir/améliorer ses performances
        successful = 0
        for i, workout in enumerate(workouts[1:], 1):  # Comparer avec la séance précédente
            prev_workout = workouts[i-1]
            
            # Considérer comme succès si maintien ou amélioration
            volume_current = workout['poids'] * workout['reps']
            volume_prev = prev_workout['poids'] * prev_workout['reps']
            
            if volume_current >= volume_prev * 0.9:  # Tolérance de 10%
                successful += 1
        
        if len(workouts) <= 1:
            return 0.7  # Valeur par défaut
            
        return successful / (len(workouts) - 1)
    
    def _get_default_weight(self) -> float:
        """Retourne un poids par défaut basé sur la machine"""
        defaults = {
            'développé': 20.0,
            'press': 25.0,
            'squat': 30.0,
            'curl': 10.0,
            'extension': 15.0,
            'rowing': 20.0,
        }
        
        machine_name = self.machine.nom.lower()
        for keyword, weight in defaults.items():
            if keyword in machine_name:
                return weight
        
        return 20.0  # Défaut général
    
    def _get_fallback_recommendation(self) -> Dict:
        """Recommandation de secours en cas d'erreur"""
        return {
            'machine_id': self.machine.id,
            'machine_nom': self.machine.nom,
            'poids_recommande': self._get_default_weight(),
            'series_recommandees': 3,
            'reps_recommandees': 10,
            'repos_recommande': 90,
            'objectif': 'DEBUTANT',
            'source': 'fallback',
            'notes': 'Recommandation de base - effectuez quelques séances pour personnaliser',
            'peut_progresser': True
        }

def get_simple_recommendation(user, machine_id: int) -> Dict:
    """
    Point d'entrée principal pour obtenir une recommandation
    """
    try:
        # Valider l'utilisateur
        if not user or not user.is_authenticated:
            return {
                'success': False,
                'error': 'Utilisateur non authentifié'
            }
        
        # Récupérer la machine
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return {
                'success': False,
                'error': f'Machine {machine_id} non trouvée'
            }
        
        # Générer la recommandation
        engine = SimpleRecommendationEngine(user, machine)
        recommendation = engine.calculate_recommendation()
        
        logger.info(f"Recommandation générée pour {user.email} - {machine.nom}: {recommendation['poids_recommande']}kg")
        
        return {
            'success': True,
            'data': recommendation
        }
        
    except Exception as e:
        logger.error(f"Erreur système recommandation: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_simple_recommendation_by_name(user, machine_name: str) -> Dict:
    """
    Point d'entrée pour obtenir une recommandation par nom de machine
    """
    try:
        # Récupérer la machine par nom
        machine = Machine.objects.filter(nom__iexact=machine_name).first()
        if not machine:
            machine = Machine.objects.filter(nom__icontains=machine_name).first()
        
        if not machine:
            return {
                'success': False,
                'error': f'Machine "{machine_name}" non trouvée'
            }
        
        return get_simple_recommendation(user, machine.id)
        
    except Exception as e:
        logger.error(f"Erreur recherche machine: {e}")
        return {
            'success': False,
            'error': str(e)
        }