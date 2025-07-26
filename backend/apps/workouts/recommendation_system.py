"""
Système de recommandation professionnel pour BasicFit
Refactorisation complète pour éliminer les bugs et améliorer les performances
"""
import logging
from typing import Dict, Optional, Tuple
from django.db import models
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class WorkoutRecommendationEngine:
    """
    Moteur de recommandation professionnel pour les entraînements
    Utilise des algorithmes basés sur la science du sport
    """
    
    # Configuration des objectifs d'entraînement
    TRAINING_GOALS = {
        'FORCE': {
            'reps_range': (1, 5),
            'sets_range': (3, 6),
            'intensity_1rm': 0.85,
            'rest_seconds': 180,
            'progression_threshold': 85.0
        },
        'PRISE_MASSE': {
            'reps_range': (6, 12),
            'sets_range': (3, 5),
            'intensity_1rm': 0.70,
            'rest_seconds': 90,
            'progression_threshold': 80.0
        },
        'ENDURANCE': {
            'reps_range': (12, 20),
            'sets_range': (2, 4),
            'intensity_1rm': 0.60,
            'rest_seconds': 60,
            'progression_threshold': 75.0
        },
        'SECHE': {
            'reps_range': (8, 15),
            'sets_range': (3, 4),
            'intensity_1rm': 0.65,
            'rest_seconds': 75,
            'progression_threshold': 78.0
        }
    }
    
    def __init__(self, user, machine):
        """
        Initialise le moteur de recommandation
        
        Args:
            user: Utilisateur Django
            machine: Machine d'exercice
        """
        self.user = user
        self.machine = machine
        self.user_goal = getattr(user, 'objectif_sportif', 'PRISE_MASSE')
        self.goal_config = self.TRAINING_GOALS.get(self.user_goal, self.TRAINING_GOALS['PRISE_MASSE'])
        
    def calculate_current_1rm(self) -> Optional[float]:
        """
        Calcule le 1RM actuel basé sur les dernières performances
        Utilise la formule de Brzycki: 1RM = weight × (36 / (37 - reps))
        """
        from .models import ExerciceSeance
        
        # Récupérer les 3 dernières séances avec cette machine
        recent_exercises = ExerciceSeance.objects.filter(
            seance__utilisateur=self.user,
            machine=self.machine,
            seance__statut='TERMINEE',
            poids_utilise__gt=0,
            repetitions_realisees__gt=0
        ).select_related('seance').order_by('-seance__date_fin')[:3]
        
        if not recent_exercises.exists():
            return None
            
        best_1rm = 0.0
        for exercise in recent_exercises:
            # Calculer 1RM pour chaque exercice
            weight = exercise.poids_utilise
            avg_reps = exercise.repetitions_realisees / max(exercise.nombre_series, 1)
            
            if weight and avg_reps and avg_reps < 37:
                estimated_1rm = weight * (36 / (37 - avg_reps))
                best_1rm = max(best_1rm, estimated_1rm)
                
        return best_1rm if best_1rm > 0 else None
    
    def analyze_recent_performance(self) -> Dict:
        """
        Analyse les performances récentes pour adapter la recommandation
        """
        from .models import ExerciceSeance, SeriExercice
        
        # Récupérer les 2 dernières séances
        recent_exercises = ExerciceSeance.objects.filter(
            seance__utilisateur=self.user,
            machine=self.machine,
            seance__statut='TERMINEE'
        ).select_related('seance').prefetch_related('series').order_by('-seance__date_fin')[:2]
        
        if not recent_exercises.exists():
            return {
                'success_rate': 0.0,
                'average_weight': self._get_base_weight(),
                'trend': 'unknown',
                'sessions_count': 0
            }
        
        # Analyser le taux de réussite
        total_sets = 0
        successful_sets = 0
        weights = []
        
        for exercise in recent_exercises:
            weights.append(exercise.poids_utilise or 0)
            
            for serie in exercise.series.all():
                total_sets += 1
                # Une série est réussie si elle atteint 80% des reps prévues
                if serie.repetitions_realisees >= serie.repetitions_prevues * 0.8:
                    successful_sets += 1
        
        success_rate = (successful_sets / total_sets * 100) if total_sets > 0 else 0
        avg_weight = sum(weights) / len(weights) if weights else self._get_base_weight()
        
        # Déterminer la tendance
        if len(weights) >= 2:
            if weights[0] > weights[1]:
                trend = 'increasing'
            elif weights[0] < weights[1]:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'success_rate': success_rate,
            'average_weight': avg_weight,
            'trend': trend,
            'sessions_count': len(recent_exercises)
        }
    
    def _get_base_weight(self) -> float:
        """Calcule un poids de base selon le groupe musculaire"""
        primary_muscles = self.machine.groupes_musculaires_primaires.all()
        
        if not primary_muscles.exists():
            return 20.0
            
        muscle_name = primary_muscles.first().nom.lower()
        
        # Poids de base selon le groupe musculaire (conservative)
        base_weights = {
            'pectoraux': 25.0,
            'dos': 30.0,
            'jambes': 40.0,
            'quadriceps': 35.0,
            'ischiojambiers': 25.0,
            'epaules': 15.0,
            'biceps': 12.0,
            'triceps': 15.0,
            'abdominaux': 10.0,
            'mollets': 30.0
        }
        
        for muscle, weight in base_weights.items():
            if muscle in muscle_name:
                return weight
                
        return 20.0
    
    def calculate_recommendation(self) -> Dict:
        """
        Calcule la recommandation complète pour la prochaine séance
        """
        current_1rm = self.calculate_current_1rm()
        performance = self.analyze_recent_performance()
        
        # Calculer le poids recommandé
        if current_1rm and current_1rm > 0:
            # Basé sur le 1RM et l'objectif
            target_weight = current_1rm * self.goal_config['intensity_1rm']
        else:
            # Première séance ou pas assez de données
            target_weight = performance['average_weight']
        
        # Ajuster selon les performances récentes
        if performance['sessions_count'] > 0:
            if performance['success_rate'] >= self.goal_config['progression_threshold']:
                # Performance excellente : augmenter
                target_weight = min(
                    target_weight + self.machine.increment_poids,
                    self.machine.poids_maximum
                )
            elif performance['success_rate'] < 60:
                # Performance faible : réduire
                target_weight = max(
                    target_weight - self.machine.increment_poids,
                    self.machine.poids_minimum
                )
            # Sinon maintenir le poids actuel
        
        # Arrondir au multiple de l'incrément
        increment = self.machine.increment_poids
        target_weight = round(target_weight / increment) * increment
        
        # S'assurer que c'est dans les limites
        target_weight = max(
            self.machine.poids_minimum,
            min(target_weight, self.machine.poids_maximum)
        )
        
        # Recommandations de séries et répétitions
        reps_min, reps_max = self.goal_config['reps_range']
        sets_min, sets_max = self.goal_config['sets_range']
        
        recommended_reps = (reps_min + reps_max) // 2
        recommended_sets = (sets_min + sets_max) // 2
        
        return {
            'machine_id': self.machine.id,
            'machine_nom': self.machine.nom,
            'poids_recommande': float(target_weight),
            'series_recommandees': recommended_sets,
            'reps_recommandees': recommended_reps,
            'repos_recommande': self.goal_config['rest_seconds'],
            'objectif': self.user_goal,
            'current_1rm': current_1rm,
            'success_rate': performance['success_rate'],
            'confidence': self._calculate_confidence(performance),
            'notes': self._generate_notes(performance, current_1rm)
        }
    
    def _calculate_confidence(self, performance: Dict) -> str:
        """Calcule le niveau de confiance de la recommandation"""
        if performance['sessions_count'] == 0:
            return 'low'
        elif performance['sessions_count'] < 3:
            return 'medium'
        else:
            return 'high'
    
    def _generate_notes(self, performance: Dict, current_1rm: Optional[float]) -> str:
        """Génère des notes explicatives pour l'utilisateur"""
        notes = []
        
        if performance['sessions_count'] == 0:
            notes.append("Première séance sur cette machine")
        elif performance['success_rate'] >= 90:
            notes.append("Excellente performance, progression possible")
        elif performance['success_rate'] < 60:
            notes.append("Performance à améliorer, poids ajusté")
        
        if current_1rm:
            notes.append(f"1RM estimé: {current_1rm:.1f}kg")
            
        return " | ".join(notes)


class RecommendationManager:
    """
    Gestionnaire centralisé pour toutes les recommandations
    """
    
    @staticmethod
    def get_recommendation_for_machine(user, machine) -> Dict:
        """
        Point d'entrée principal pour obtenir une recommandation
        """
        try:
            engine = WorkoutRecommendationEngine(user, machine)
            recommendation = engine.calculate_recommendation()
            
            logger.info(f"Recommandation générée pour {user.email} - {machine.nom}: {recommendation['poids_recommande']}kg")
            
            return {
                'success': True,
                'data': recommendation
            }
            
        except Exception as e:
            logger.error(f"Erreur génération recommandation: {e}")
            
            # Recommandation de secours
            return {
                'success': False,
                'data': {
                    'machine_id': machine.id,
                    'machine_nom': machine.nom,
                    'poids_recommande': 20.0,
                    'series_recommandees': 3,
                    'reps_recommandees': 10,
                    'repos_recommande': 90,
                    'objectif': 'PRISE_MASSE',
                    'current_1rm': None,
                    'success_rate': 0.0,
                    'confidence': 'low',
                    'notes': 'Recommandation de base'
                },
                'error': str(e)
            }
    
    @staticmethod
    def get_recommendations_for_workout(user, machine_ids: list) -> Dict:
        """
        Obtient les recommandations pour plusieurs machines (pour un entraînement complet)
        """
        from .models import Machine
        
        recommendations = {}
        
        for machine_id in machine_ids:
            try:
                machine = Machine.objects.get(id=machine_id)
                rec = RecommendationManager.get_recommendation_for_machine(user, machine)
                recommendations[machine_id] = rec
            except Machine.DoesNotExist:
                recommendations[machine_id] = {
                    'success': False,
                    'error': 'Machine non trouvée'
                }
        
        return recommendations
    
    @staticmethod
    def update_progression_after_workout(user, exercise_data: Dict):
        """
        Met à jour la progression après une séance
        Cette méthode est appelée automatiquement lors de la sauvegarde
        """
        try:
            # Cette logique sera intégrée directement dans la sauvegarde
            # pour éviter les doubles traitements
            pass
            
        except Exception as e:
            logger.error(f"Erreur mise à jour progression: {e}")