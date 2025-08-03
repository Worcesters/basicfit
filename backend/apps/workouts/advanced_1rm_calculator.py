"""
Système de calcul 1RM professionnel avec plusieurs formules et adaptation du volume
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class WorkoutData:
    """Structure pour les données d'entraînement"""
    poids: float
    reps: int
    sets: int
    tempo: str = ""
    fatigue_factor: float = 1.0  # Facteur de fatigue entre séries


class Advanced1RMCalculator:
    """
    Calculateur 1RM professionnel utilisant plusieurs formules et méthodes
    """
    
    def __init__(self):
        self.formulas = {
            'brzycki': self._brzycki,
            'epley': self._epley,
            'lander': self._lander,
            'lombardi': self._lombardi,
            'mayhew': self._mayhew,
            'oconnor': self._oconnor,
            'wathen': self._wathen,
            'baechle': self._baechle
        }
    
    def calculate_comprehensive_1rm(self, workout_data: WorkoutData) -> Dict:
        """
        Calcule le 1RM avec plusieurs formules et retourne la meilleure estimation
        """
        if workout_data.reps >= 30:
            return {
                'estimated_1rm': None,
                'reliability': 'low',
                'message': 'Trop de répétitions pour un calcul 1RM fiable'
            }
        
        # Calculer avec toutes les formules applicables
        estimates = {}
        for name, formula in self.formulas.items():
            try:
                estimate = formula(workout_data.poids, workout_data.reps)
                if estimate and estimate > 0:
                    estimates[name] = estimate
            except (ValueError, ZeroDivisionError):
                continue
        
        if not estimates:
            return {
                'estimated_1rm': None,
                'reliability': 'none',
                'message': 'Impossible de calculer le 1RM'
            }
        
        # Calcul avec ajustement de fatigue pour séries multiples
        fatigue_adjusted_1rm = self._adjust_for_fatigue(workout_data, estimates)
        
        # Déterminer la fiabilité
        reliability = self._determine_reliability(workout_data.reps, len(estimates))
        
        # Prendre la médiane pour robustesse
        sorted_estimates = sorted(estimates.values())
        median_1rm = sorted_estimates[len(sorted_estimates) // 2]
        
        return {
            'estimated_1rm': round(fatigue_adjusted_1rm, 1),
            'raw_estimates': estimates,
            'median_estimate': round(median_1rm, 1),
            'reliability': reliability,
            'confidence_range': self._calculate_confidence_range(sorted_estimates),
            'volume_total': workout_data.poids * workout_data.reps * workout_data.sets,
            'message': f'1RM estimé avec {len(estimates)} formules'
        }
    
    def calculate_volume_equivalent_weights(self, current_workout: WorkoutData, target_reps: int, target_sets: int) -> Dict:
        """
        Calcule le poids équivalent pour maintenir le même volume de travail
        """
        # Calcul du 1RM actuel
        one_rm_result = self.calculate_comprehensive_1rm(current_workout)
        
        if not one_rm_result['estimated_1rm']:
            return {
                'success': False,
                'message': 'Impossible de calculer le 1RM de référence'
            }
        
        estimated_1rm = one_rm_result['estimated_1rm']
        current_volume = current_workout.poids * current_workout.reps * current_workout.sets
        
        # Calculer le pourcentage 1RM actuel
        current_intensity = (current_workout.poids / estimated_1rm) * 100
        
        # Calcul du poids cible pour maintenir l'intensité relative
        intensity_based_weight = estimated_1rm * (current_intensity / 100)
        
        # Calcul du poids pour maintenir le volume total
        target_volume_per_rep = current_volume / (target_reps * target_sets)
        volume_based_weight = target_volume_per_rep
        
        # Compromis entre intensité et volume (70% intensité, 30% volume)
        recommended_weight = (intensity_based_weight * 0.7) + (volume_based_weight * 0.3)
        
        # Ajustement physiologique selon le nombre de répétitions
        physiological_adjustment = self._get_physiological_adjustment(target_reps)
        final_weight = recommended_weight * physiological_adjustment
        
        return {
            'success': True,
            'recommended_weight': round(final_weight, 1),
            'estimated_1rm': estimated_1rm,
            'current_intensity_percent': round(current_intensity, 1),
            'target_intensity_percent': round((final_weight / estimated_1rm) * 100, 1),
            'current_volume': current_volume,
            'target_volume': round(final_weight * target_reps * target_sets, 1),
            'volume_ratio': round((final_weight * target_reps * target_sets) / current_volume, 2),
            'intensity_based_weight': round(intensity_based_weight, 1),
            'volume_based_weight': round(volume_based_weight, 1),
            'physiological_factor': physiological_adjustment
        }
    
    def _brzycki(self, weight: float, reps: int) -> float:
        """Formule de Brzycki : 1RM = weight × (36 / (37 - reps))"""
        if reps >= 37:
            raise ValueError("Trop de répétitions pour Brzycki")
        return weight * (36 / (37 - reps))
    
    def _epley(self, weight: float, reps: int) -> float:
        """Formule d'Epley : 1RM = weight × (1 + 0.0333 × reps)"""
        return weight * (1 + 0.0333 * reps)
    
    def _lander(self, weight: float, reps: int) -> float:
        """Formule de Lander : 1RM = (100 × weight) / (101.3 - 2.67123 × reps)"""
        denominator = 101.3 - 2.67123 * reps
        if denominator <= 0:
            raise ValueError("Trop de répétitions pour Lander")
        return (100 * weight) / denominator
    
    def _lombardi(self, weight: float, reps: int) -> float:
        """Formule de Lombardi : 1RM = weight × reps^0.1"""
        return weight * (reps ** 0.1)
    
    def _mayhew(self, weight: float, reps: int) -> float:
        """Formule de Mayhew : 1RM = (100 × weight) / (52.2 + 41.9 × e^(-0.055 × reps))"""
        exp_term = math.exp(-0.055 * reps)
        denominator = 52.2 + 41.9 * exp_term
        return (100 * weight) / denominator
    
    def _oconnor(self, weight: float, reps: int) -> float:
        """Formule d'O'Connor : 1RM = weight × (1 + 0.025 × reps)"""
        return weight * (1 + 0.025 * reps)
    
    def _wathen(self, weight: float, reps: int) -> float:
        """Formule de Wathen : 1RM = (100 × weight) / (48.8 + 53.8 × e^(-0.075 × reps))"""
        exp_term = math.exp(-0.075 * reps)
        denominator = 48.8 + 53.8 * exp_term
        return (100 * weight) / denominator
    
    def _baechle(self, weight: float, reps: int) -> float:
        """Formule de Baechle & Earle : basée sur %1RM standards"""
        # Table de correspondance répétitions -> %1RM
        percent_1rm_table = {
            1: 100, 2: 97, 3: 94, 4: 92, 5: 89, 6: 86, 7: 83, 8: 81,
            9: 78, 10: 75, 11: 73, 12: 71, 13: 70, 14: 68, 15: 67,
            16: 65, 17: 64, 18: 63, 19: 61, 20: 60
        }
        
        if reps > 20:
            # Extrapolation pour plus de 20 reps
            percent = max(40, 60 - (reps - 20) * 1.5)
        else:
            percent = percent_1rm_table.get(reps, 60)
        
        return (weight * 100) / percent
    
    def _adjust_for_fatigue(self, workout_data: WorkoutData, estimates: Dict) -> float:
        """
        Ajuste le 1RM calculé en fonction de la fatigue accumulée sur plusieurs séries
        """
        if workout_data.sets <= 1:
            return sum(estimates.values()) / len(estimates)
        
        # Facteur de fatigue progressif par série
        base_estimate = sum(estimates.values()) / len(estimates)
        
        # Plus de séries = plus de fatigue = 1RM réel probablement plus élevé
        fatigue_factors = {
            2: 1.02,  # 2% de bonus
            3: 1.04,  # 4% de bonus  
            4: 1.06,  # 6% de bonus
            5: 1.08,  # 8% de bonus
        }
        
        sets = min(workout_data.sets, 5)
        adjustment = fatigue_factors.get(sets, 1.10)  # 10% pour 6+ séries
        
        return base_estimate * adjustment
    
    def _determine_reliability(self, reps: int, num_formulas: int) -> str:
        """Détermine la fiabilité de l'estimation"""
        if reps <= 3:
            return 'high'
        elif reps <= 6:
            return 'very_good'
        elif reps <= 10:
            return 'good'
        elif reps <= 15:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_confidence_range(self, estimates: List[float]) -> Dict:
        """Calcule l'intervalle de confiance"""
        if len(estimates) < 2:
            return {'min': estimates[0], 'max': estimates[0], 'spread': 0}
        
        min_est = min(estimates)
        max_est = max(estimates)
        spread = max_est - min_est
        
        return {
            'min': round(min_est, 1),
            'max': round(max_est, 1),
            'spread': round(spread, 1)
        }
    
    def _get_physiological_adjustment(self, target_reps: int) -> float:
        """
        Ajustement physiologique selon la zone de répétitions cible
        Basé sur les adaptations neuromusculaires spécifiques
        """
        # Force/Power (1-5 reps) : système phosphocréatine
        if target_reps <= 5:
            return 1.05  # +5% car sollicitation neuromusculaire maximale
        
        # Hypertrophie (6-12 reps) : équilibre métabolique/mécanique
        elif target_reps <= 12:
            return 1.0  # Référence
        
        # Endurance de force (13-20 reps) : système glycolytique
        elif target_reps <= 20:
            return 0.92  # -8% car moins d'intensité, plus de volume
        
        # Endurance (20+ reps) : système aérobie
        else:
            return 0.85  # -15% car beaucoup moins d'intensité


# Fonction utilitaire pour l'intégration
def calculate_professional_recommendation(current_weight: float, current_reps: int, current_sets: int, 
                                        target_reps: int, target_sets: int, tempo: str = "") -> Dict:
    """
    Point d'entrée principal pour le calcul professionnel de recommandation
    """
    calculator = Advanced1RMCalculator()
    
    # Créer les données d'entraînement actuelles
    current_workout = WorkoutData(
        poids=current_weight,
        reps=current_reps, 
        sets=current_sets,
        tempo=tempo
    )
    
    # Calculer la recommandation
    recommendation = calculator.calculate_volume_equivalent_weights(
        current_workout, target_reps, target_sets
    )
    
    if not recommendation['success']:
        return recommendation
    
    # Ajouter des informations détaillées
    one_rm_analysis = calculator.calculate_comprehensive_1rm(current_workout)
    
    return {
        **recommendation,
        'one_rm_analysis': one_rm_analysis,
        'current_workout': {
            'weight': current_weight,
            'reps': current_reps, 
            'sets': current_sets,
            'total_volume': current_weight * current_reps * current_sets
        },
        'target_workout': {
            'weight': recommendation['recommended_weight'],
            'reps': target_reps,
            'sets': target_sets,
            'total_volume': recommendation['target_volume']
        }
    }