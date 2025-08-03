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
from .advanced_1rm_calculator import calculate_professional_recommendation

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
            
            # 2. Vérifier s'il y a des données d'entraînement
            has_workout_data = bool(progression and progression.poids_actuel > 0) or bool(recent_workouts)
            
            if not has_workout_data:
                # Aucune donnée d'entraînement trouvée
                logger.info(f"Aucune séance trouvée pour {self.machine.nom}")
                return self._get_no_data_response()
            
            # 3. Déterminer le poids de base
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
                # Ne devrait pas arriver grâce à la vérification has_workout_data
                return self._get_no_data_response()
            
            # 4. Calculer la progression avec système professionnel
            recommended_weight, recommended_reps, recommended_sets, calculation_details = self._calculate_professional_progression(
                base_weight, base_reps, base_sets, progression, recent_workouts
            )
            
            # 5. Retourner la recommandation (format compatible Android)
            return {
                'machine_id': self.machine.id,
                'machine_nom': self.machine.nom,
                'poids_recommande': recommended_weight,
                'series_recommandees': recommended_sets,
                'reps_recommandees': recommended_reps,
                'repos_recommande': 90,
                'objectif': 'PROGRESSION',
                'source': source,
                'notes': self._generate_professional_notes(calculation_details, source),
                'peut_progresser': True,
                'tempo_recommande': self.machine.tempo or "3-1-2",  # Ajout du tempo
                # Champs compatibilité Android
                'dernier_1rm': calculation_details.get('estimated_1rm') if calculation_details else (progression.dernier_1rm if progression else None),
                'nombre_seances': progression.nombre_seances_machine if progression else 0,
                'progression_totale': recommended_weight - base_weight if progression else 0.0,
                'taux_reussite': progression.taux_reussite if progression else 0.0,
                'derniere_progression': source,
                # Détails du calcul professionnel
                'calcul_1rm_details': calculation_details,
                'volume_precedent': base_weight * base_reps * base_sets,
                'volume_recommande': recommended_weight * recommended_reps * recommended_sets
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul recommandation: {e}")
            return self._get_fallback_recommendation()
    
    def _calculate_professional_progression(self, base_weight: float, base_reps: int, base_sets: int, 
                                          progression: ProgressionMachine, recent_workouts: list) -> tuple:
        """
        Calcule la progression avec le système professionnel 1RM
        Retourne (poids, reps, sets, details_calcul)
        """
        try:
            # Analyser les performances récentes pour déterminer la stratégie
            success_rate = self._calculate_success_rate(recent_workouts)
            
            # Déterminer les répétitions et séries cibles selon l'objectif
            if hasattr(self.user, 'profil_fitness') and self.user.profil_fitness:
                objectif = self.user.profil_fitness.objectif_principal
            else:
                objectif = 'PRISE_MASSE'  # Par défaut
            
            target_reps, target_sets = self._get_target_reps_sets(objectif, success_rate)
            
            # Utiliser le calculateur professionnel
            if base_reps > 0 and base_sets > 0:
                machine_tempo = getattr(self.machine, 'tempo', '3-1-2')
                
                professional_calc = calculate_professional_recommendation(
                    current_weight=base_weight,
                    current_reps=base_reps,
                    current_sets=base_sets,
                    target_reps=target_reps,
                    target_sets=target_sets,
                    tempo=machine_tempo
                )
                
                if professional_calc.get('success'):
                    recommended_weight = professional_calc['recommended_weight']
                    
                    # Ajustement selon le taux de réussite
                    if success_rate >= 0.8:  # Très bon
                        weight_adjustment = 1.0  # Aucun ajustement
                    elif success_rate >= 0.6:  # Moyen
                        weight_adjustment = 0.95  # -5%
                    else:  # Faible
                        weight_adjustment = 0.90  # -10%
                    
                    final_weight = recommended_weight * weight_adjustment
                    
                    return (
                        round(final_weight, 1),
                        target_reps,
                        target_sets,
                        professional_calc
                    )
            
            # Fallback vers l'ancienne méthode
            return (
                self._calculate_progression(base_weight, progression, recent_workouts),
                min(12, max(8, base_reps)),
                min(4, max(3, base_sets)),
                {'success': False, 'method': 'fallback'}
            )
            
        except Exception as e:
            logger.error(f"Erreur calcul professionnel: {e}")
            # Fallback
            return (
                base_weight,
                base_reps,
                base_sets,
                {'success': False, 'error': str(e)}
            )
    
    def _get_target_reps_sets(self, objectif: str, success_rate: float) -> tuple:
        """Détermine les répétitions et séries cibles selon l'objectif"""
        targets = {
            'FORCE': (5, 4),
            'PRISE_MASSE': (10, 4),
            'SECHE': (12, 3),
            'ENDURANCE': (15, 3),
            'POWERLIFTING': (3, 5)
        }
        
        base_reps, base_sets = targets.get(objectif, (10, 3))
        
        # Ajustement selon le taux de réussite
        if success_rate < 0.6:
            # Réduire l'intensité : plus de reps, moins de séries
            base_reps += 2
            base_sets = max(2, base_sets - 1)
        elif success_rate > 0.8:
            # Augmenter l'intensité : moins de reps, plus de séries
            base_reps = max(3, base_reps - 1)
            base_sets = min(5, base_sets + 1)
        
        return base_reps, base_sets
    
    def _generate_professional_notes(self, calculation_details: dict, source: str) -> str:
        """Génère des notes détaillées sur le calcul professionnel"""
        if not calculation_details or not calculation_details.get('success'):
            return f"Basé sur {source} (méthode classique)"
        
        notes = []
        notes.append(f"Basé sur {source}")
        
        if '1rm_analysis' in calculation_details:
            analysis = calculation_details['1rm_analysis']
            if analysis.get('estimated_1rm'):
                notes.append(f"1RM estimé: {analysis['estimated_1rm']}kg")
                notes.append(f"Fiabilité: {analysis.get('reliability', 'inconnue')}")
        
        if 'volume_ratio' in calculation_details:
            ratio = calculation_details['volume_ratio']
            if ratio > 1.1:
                notes.append("Volume augmenté pour progression")
            elif ratio < 0.9:
                notes.append("Volume réduit pour récupération")
            else:
                notes.append("Volume maintenu")
        
        return " | ".join(notes)
    
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
    
    def _get_no_data_response(self) -> Dict:
        """Réponse quand aucune donnée d'entraînement n'est trouvée"""
        return {
            'machine_id': self.machine.id,
            'machine_nom': self.machine.nom,
            'poids_recommande': None,
            'series_recommandees': None,
            'reps_recommandees': None,
            'repos_recommande': None,
            'objectif': 'AUCUNE_DONNEE',
            'source': 'no_data',
            'notes': 'Aucune recommandation pour cette machine',
            'peut_progresser': False,
            'message': 'Aucune recommandation pour cette machine',
            # Champs compatibilité Android
            'dernier_1rm': None,
            'nombre_seances': 0,
            'progression_totale': 0.0,
            'taux_reussite': 0.0,
            'derniere_progression': 'no_data'
        }

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
            'peut_progresser': True,
            # Champs compatibilité Android
            'dernier_1rm': None,
            'nombre_seances': 0,
            'progression_totale': 0.0,
            'taux_reussite': 0.0,
            'derniere_progression': 'fallback'
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


def get_generic_recommendation(machine_id: int) -> Dict:
    """
    Génère une recommandation générique pour un utilisateur non authentifié
    """
    try:
        machine = Machine.objects.get(id=machine_id)
        return _generate_generic_recommendation(machine)
    except Machine.DoesNotExist:
        return {
            'success': False,
            'error': f'Machine avec ID {machine_id} non trouvée'
        }
    except Exception as e:
        logger.error(f"Erreur recommandation générique ID {machine_id}: {e}")
        return {
            'success': False,
            'error': f'Erreur lors du calcul de la recommandation: {str(e)}'
        }


def get_generic_recommendation_by_name(machine_name: str) -> Dict:
    """
    Génère une recommandation générique par nom de machine
    """
    try:
        # Recherche flexible par nom
        try:
            machine = Machine.objects.get(nom__iexact=machine_name)
        except Machine.DoesNotExist:
            try:
                machine = Machine.objects.get(nom__icontains=machine_name)
            except Machine.DoesNotExist:
                # Essayer avec des variations courantes
                variations = [
                    machine_name.replace('é', 'e').replace('è', 'e'),
                    machine_name.replace('e', 'é'),
                    machine_name.replace('e', 'è'),
                ]
                for variation in variations:
                    try:
                        machine = Machine.objects.get(nom__icontains=variation)
                        break
                    except Machine.DoesNotExist:
                        continue
                else:
                    return {
                        'success': False,
                        'error': f'Machine "{machine_name}" non trouvée'
                    }
        
        return _generate_generic_recommendation(machine)
    except Exception as e:
        logger.error(f"Erreur recommandation générique nom {machine_name}: {e}")
        return {
            'success': False,
            'error': f'Erreur lors du calcul de la recommandation: {str(e)}'
        }


def _generate_generic_recommendation(machine: Machine) -> Dict:
    """
    Génère une recommandation générique basée sur les caractéristiques de la machine
    """
    # Détecter le groupe musculaire principal
    groupes_primaires = machine.groupes_musculaires_primaires.all()
    groupe_principal = groupes_primaires.first() if groupes_primaires.exists() else None

    # Poids de base selon le groupe musculaire (valeurs conservatives pour débutants)
    if groupe_principal:
        groupe_nom = groupe_principal.nom.lower()
        if 'pectoraux' in groupe_nom or 'chest' in groupe_nom:
            poids_base = 20.0
            reps = 10
            series = 3
        elif 'dos' in groupe_nom or 'back' in groupe_nom:
            poids_base = 18.0
            reps = 10
            series = 3
        elif 'jambes' in groupe_nom or 'cuisses' in groupe_nom or 'leg' in groupe_nom:
            poids_base = 30.0
            reps = 12
            series = 3
        elif 'epaules' in groupe_nom or 'shoulder' in groupe_nom:
            poids_base = 12.0
            reps = 12
            series = 3
        elif 'bras' in groupe_nom or 'biceps' in groupe_nom or 'triceps' in groupe_nom:
            poids_base = 8.0
            reps = 12
            series = 3
        else:
            poids_base = 15.0
            reps = 10
            series = 3
    else:
        # Valeurs par défaut
        poids_base = 15.0
        reps = 10
        series = 3

    # Vérifier si c'est une machine cardio
    if machine.categorie and 'cardio' in machine.categorie.nom.lower():
        poids_base = 0.0
        reps = 20  # 20 minutes
        series = 1

    return {
        'success': True,
        'data': {
            'machine_id': machine.id,
            'machine_nom': machine.nom,
            'poids_recommande': poids_base,
            'series_recommandees': series,
            'reps_recommandees': reps,
            'repos_recommande': 90,
            'objectif': 'DEBUTANT',
            'peut_progresser': True,
            'dernier_1rm': None,
            'nombre_seances': 0,
            'progression_totale': 0.0,
            'taux_reussite': 0.0,
            'derniere_progression': None,
            'source': 'recommandation_generique',
            'notes': f"Recommandation générique pour débutant • Technique d'abord • Progression graduelle",
            'tempo_recommande': machine.tempo or "3-1-2"
        }
    }