"""
Nouveau système de recommandation basé exclusivement sur la progression en base de données
Utilise les données de ProgressionMachine pour proposer des recommandations logiques
en fonction du type de session sélectionné (endurance, volume, force)
"""
from typing import Dict, List, Optional
from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from datetime import timedelta

from .models import ProgressionMachine, ExerciceSeance, SeanceEntrainement
from apps.core.models import ModeEntrainement
from apps.machines.models import Machine
from apps.users.models import User


class ProgressionBasedRecommendationSystem:
    """
    Système de recommandation basé sur la progression réelle de l'utilisateur
    """

    def __init__(self):
        # Configuration des modes d'entraînement
        self.mode_configs = {
            'FORCE': {
                'series_min': 3,
                'series_max': 5,
                'reps_min': 1,
                'reps_max': 6,
                'repos_min': 180,  # 3 minutes
                'repos_max': 300,  # 5 minutes
                'intensite': 0.85,  # 85% du 1RM
                'progression_seuil': 90.0  # Seuil de réussite pour progresser
            },
            'PRISE_MASSE': {
                'series_min': 3,
                'series_max': 4,
                'reps_min': 8,
                'reps_max': 15,
                'repos_min': 90,   # 1.5 minutes
                'repos_max': 120,  # 2 minutes
                'intensite': 0.70,  # 70% du 1RM
                'progression_seuil': 85.0
            },
            'ENDURANCE': {
                'series_min': 2,
                'series_max': 4,
                'reps_min': 15,
                'reps_max': 25,
                'repos_min': 60,   # 1 minute
                'repos_max': 90,   # 1.5 minutes
                'intensite': 0.50,  # 50% du 1RM
                'progression_seuil': 80.0
            },
            'SECHE': {
                'series_min': 3,
                'series_max': 5,
                'reps_min': 12,
                'reps_max': 20,
                'repos_min': 60,   # 1 minute
                'repos_max': 90,   # 1.5 minutes
                'intensite': 0.60,  # 60% du 1RM
                'progression_seuil': 85.0
            }
        }

    def get_recommendations_for_user(self, user: User, mode_entrainement: str,
                                   nb_machines: int = 6) -> List[Dict]:
        """
        Génère des recommandations pour un utilisateur basées sur sa progression

        Args:
            user: L'utilisateur
            mode_entrainement: Type de session ('FORCE', 'PRISE_MASSE', 'ENDURANCE', 'SECHE')
            nb_machines: Nombre de machines à recommander

        Returns:
            Liste des recommandations avec machine, poids, séries, reps, etc.
        """
        if mode_entrainement not in self.mode_configs:
            raise ValueError(f"Mode d'entraînement non supporté: {mode_entrainement}")

        config = self.mode_configs[mode_entrainement]

        # Récupérer le mode d'entraînement depuis la DB
        try:
            mode_obj = ModeEntrainement.objects.get(nom=mode_entrainement)
        except ModeEntrainement.DoesNotExist:
            # Créer le mode s'il n'existe pas
            mode_obj = self._create_mode_entrainement(mode_entrainement, config)

        # Récupérer toutes les progressions de l'utilisateur
        progressions = ProgressionMachine.objects.filter(
            utilisateur=user,
            mode_entrainement=mode_obj
        ).select_related('machine')

        recommendations = []

        # Si l'utilisateur a des progressions, utiliser ces données
        if progressions.exists():
            recommendations = self._get_recommendations_from_progressions(
                progressions, config, nb_machines
            )
        else:
            # Première utilisation : recommandations par défaut basées sur le profil
            recommendations = self._get_default_recommendations(
                user, mode_obj, config, nb_machines
            )

        return recommendations

    def _get_recommendations_from_progressions(self, progressions, config: Dict,
                                             nb_machines: int) -> List[Dict]:
        """
        Génère des recommandations basées sur les progressions existantes
        """
        recommendations = []

        # Trier les progressions par performance et variété
        progressions_list = list(progressions)
        progressions_list.sort(key=lambda p: (
            p.taux_reussite,  # Taux de réussite
            p.nombre_seances_machine,  # Expérience sur la machine
            -p.derniere_progression.timestamp() if p.derniere_progression else 0
        ), reverse=True)

        for progression in progressions_list[:nb_machines]:
            recommendation = self._generate_recommendation_from_progression(
                progression, config
            )
            recommendations.append(recommendation)

        # Compléter avec de nouvelles machines si nécessaire
        if len(recommendations) < nb_machines:
            machines_utilisees = {r['machine_id'] for r in recommendations}
            nouvelles_machines = self._get_new_machines_recommendations(
                progression.utilisateur, config,
                nb_machines - len(recommendations), machines_utilisees
            )
            recommendations.extend(nouvelles_machines)

        return recommendations

    def _generate_recommendation_from_progression(self, progression: ProgressionMachine,
                                                config: Dict) -> Dict:
        """
        Génère une recommandation basée sur une progression existante
        """
        machine = progression.machine

        # Calculer le poids recommandé
        poids_recommande = self._calculate_recommended_weight(progression, config)

        # Calculer séries et répétitions selon le mode
        series = self._calculate_series(progression, config)
        reps = self._calculate_reps(progression, config)
        repos = self._calculate_rest_time(config)

        # Générer des notes explicatives
        notes = self._generate_recommendation_notes(progression, config)

        return {
            'machine_id': machine.id,
            'machine_nom': machine.nom,
            'machine_categorie': machine.categorie.nom if machine.categorie else 'Autre',
            'poids_recommande': poids_recommande,
            'series_recommandees': series,
            'repetitions_recommandees': reps,
            'repos_recommande': repos,
            'notes': notes,
            'progression_info': {
                'poids_actuel': progression.poids_actuel,
                'taux_reussite': progression.taux_reussite,
                'nombre_seances': progression.nombre_seances_machine,
                'dernier_1rm': progression.dernier_1rm,
                'progression_totale': progression.progression_poids_total
            },
            'recommandation_source': 'progression_existante'
        }

    def _calculate_recommended_weight(self, progression: ProgressionMachine,
                                    config: Dict) -> float:
        """
        Calcule le poids recommandé basé sur la progression et le mode d'entraînement
        """
        poids_actuel = progression.poids_actuel
        taux_reussite = progression.taux_reussite
        seuil_progression = config['progression_seuil']
        increment = progression.machine.increment_poids

        # Logique de progression basée sur le taux de réussite
        if taux_reussite >= seuil_progression:
            # Excellent taux : augmentation
            nouveau_poids = poids_actuel + increment
            # Vérifier les limites de la machine
            if nouveau_poids <= progression.machine.poids_maximum:
                return nouveau_poids
            else:
                return progression.machine.poids_maximum

        elif taux_reussite >= 70.0:
            # Bon taux : maintien du poids
            return poids_actuel

        elif taux_reussite >= 50.0:
            # Taux moyen : léger ajustement ou maintien
            return poids_actuel

        else:
            # Faible taux : diminution pour améliorer la technique
            nouveau_poids = poids_actuel - increment
            if nouveau_poids >= progression.machine.poids_minimum:
                return nouveau_poids
            else:
                return progression.machine.poids_minimum

    def _calculate_series(self, progression: ProgressionMachine, config: Dict) -> int:
        """
        Calcule le nombre de séries recommandées
        """
        # Utiliser la configuration du mode d'entraînement
        series_min = config['series_min']
        series_max = config['series_max']

        # Ajuster selon l'expérience de l'utilisateur
        if progression.nombre_seances_machine <= 5:
            # Débutant sur cette machine : commencer doucement
            return series_min
        elif progression.taux_reussite >= 85.0:
            # Très bon taux : peut faire plus de séries
            return series_max
        else:
            # Taux moyen : nombre de séries moyen
            return (series_min + series_max) // 2

    def _calculate_reps(self, progression: ProgressionMachine, config: Dict) -> int:
        """
        Calcule le nombre de répétitions recommandées
        """
        reps_min = config['reps_min']
        reps_max = config['reps_max']

        # Ajuster selon l'expérience et la performance
        if progression.nombre_seances_machine <= 3:
            # Débutant : plus de répétitions pour apprendre le mouvement
            return reps_max
        elif progression.taux_reussite >= 90.0:
            # Excellent taux : peut essayer moins de reps avec plus de poids
            return reps_min
        else:
            # Taux moyen : répétitions moyennes
            return (reps_min + reps_max) // 2

    def _calculate_rest_time(self, config: Dict) -> int:
        """
        Calcule le temps de repos recommandé
        """
        return (config['repos_min'] + config['repos_max']) // 2

    def _generate_recommendation_notes(self, progression: ProgressionMachine,
                                     config: Dict) -> str:
        """
        Génère des notes explicatives pour la recommandation
        """
        taux = progression.taux_reussite

        if taux >= config['progression_seuil']:
            return f"Excellent travail ! Taux de réussite: {taux:.1f}%. Augmentation du poids recommandée."
        elif taux >= 70.0:
            return f"Bonne progression (taux: {taux:.1f}%). Maintien du poids pour consolider."
        elif taux >= 50.0:
            return f"Progression correcte (taux: {taux:.1f}%). Travail de stabilisation recommandé."
        else:
            return f"Difficultés rencontrées (taux: {taux:.1f}%). Réduction du poids pour améliorer la technique."

    def _get_default_recommendations(self, user: User, mode_obj: ModeEntrainement,
                                   config: Dict, nb_machines: int) -> List[Dict]:
        """
        Génère des recommandations par défaut pour un nouvel utilisateur
        """
        # Sélectionner des machines variées selon les groupes musculaires
        machines = Machine.objects.filter(
            is_active=True
        ).select_related('categorie')[:nb_machines * 2]  # Prendre plus pour avoir du choix

        recommendations = []
        groupes_utilises = set()

        for machine in machines:
            if len(recommendations) >= nb_machines:
                break

            # Éviter de répéter les mêmes groupes musculaires
            if machine.categorie and machine.categorie.nom in groupes_utilises:
                continue

            # Calculer un poids de départ basé sur le profil utilisateur
            poids_depart = self._calculate_starting_weight(user, machine, config)

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'machine_categorie': machine.categorie.nom if machine.categorie else 'Autre',
                'poids_recommande': poids_depart,
                'series_recommandees': config['series_min'],
                'repetitions_recommandees': config['reps_max'],  # Plus de reps pour débuter
                'repos_recommande': config['repos_max'],  # Plus de repos pour débuter
                'notes': f"Première session sur cette machine. Commencez léger pour apprendre le mouvement.",
                'progression_info': {
                    'poids_actuel': 0,
                    'taux_reussite': 0,
                    'nombre_seances': 0,
                    'dernier_1rm': None,
                    'progression_totale': 0
                },
                'recommandation_source': 'premiere_utilisation'
            }

            recommendations.append(recommendation)
            if machine.categorie:
                groupes_utilises.add(machine.categorie.nom)

        return recommendations

    def _calculate_starting_weight(self, user: User, machine: Machine, config: Dict) -> float:
        """
        Calcule un poids de départ pour un utilisateur sur une nouvelle machine
        """
        # Poids de base selon le sexe et l'expérience
        if hasattr(user, 'profil_fitness'):
            if user.profil_fitness.sexe == 'M':
                base_weight = machine.poids_minimum + (machine.increment_poids * 3)
            else:
                base_weight = machine.poids_minimum + (machine.increment_poids * 2)
        else:
            base_weight = machine.poids_minimum + machine.increment_poids

        # S'assurer que c'est dans les limites de la machine
        return min(max(base_weight, machine.poids_minimum), machine.poids_maximum)

    def _get_new_machines_recommendations(self, user: User, config: Dict,
                                        nb_needed: int, machines_utilisees: set) -> List[Dict]:
        """
        Recommande de nouvelles machines non encore utilisées
        """
        nouvelles_machines = Machine.objects.filter(
            is_active=True
        ).exclude(id__in=machines_utilisees)[:nb_needed]

        recommendations = []
        for machine in nouvelles_machines:
            poids_depart = self._calculate_starting_weight(user, machine, config)

            recommendation = {
                'machine_id': machine.id,
                'machine_nom': machine.nom,
                'machine_categorie': machine.categorie.nom if machine.categorie else 'Autre',
                'poids_recommande': poids_depart,
                'series_recommandees': config['series_min'],
                'repetitions_recommandees': config['reps_max'],
                'repos_recommande': config['repos_max'],
                'notes': f"Nouvelle machine recommandée pour diversifier l'entraînement.",
                'progression_info': {
                    'poids_actuel': 0,
                    'taux_reussite': 0,
                    'nombre_seances': 0,
                    'dernier_1rm': None,
                    'progression_totale': 0
                },
                'recommandation_source': 'nouvelle_machine'
            }
            recommendations.append(recommendation)

        return recommendations

    def _create_mode_entrainement(self, nom: str, config: Dict) -> ModeEntrainement:
        """
        Crée un mode d'entraînement s'il n'existe pas
        """
        descriptions = {
            'FORCE': 'Développement de la force maximale avec charges lourdes',
            'PRISE_MASSE': 'Développement de la masse musculaire avec volume modéré',
            'ENDURANCE': 'Développement de l\'endurance musculaire avec charges légères',
            'SECHE': 'Maintien musculaire en période de sèche avec volume élevé'
        }

        return ModeEntrainement.objects.create(
            nom=nom,
            description=descriptions.get(nom, ''),
            series_recommandees=config['series_min'],
            repetitions_min=config['reps_min'],
            repetitions_max=config['reps_max'],
            repos_entre_series=config['repos_min'],
            pourcentage_1rm_min=config['intensite'] - 0.1,
            pourcentage_1rm_max=config['intensite'] + 0.1
        )

    def update_progression_after_workout(self, seance: SeanceEntrainement):
        """
        Met à jour les progressions après une séance d'entraînement
        """
        for exercice in seance.exercices.all():
            self._update_machine_progression(exercice)

    def _update_machine_progression(self, exercice: ExerciceSeance):
        """
        Met à jour la progression pour une machine après un exercice
        """
        try:
            progression = ProgressionMachine.objects.get(
                utilisateur=exercice.seance.utilisateur,
                machine=exercice.machine,
                mode_entrainement=exercice.seance.mode_entrainement
            )
        except ProgressionMachine.DoesNotExist:
            # Créer une nouvelle progression
            progression = ProgressionMachine.objects.create(
                utilisateur=exercice.seance.utilisateur,
                machine=exercice.machine,
                mode_entrainement=exercice.seance.mode_entrainement,
                poids_actuel=exercice.poids_utilise or exercice.poids_prevu,
                series_actuelles=exercice.series_prevues,
                repetitions_actuelles=exercice.repetitions_prevues
            )

        # Calculer le taux de réussite de cette session
        series_reussies = sum(1 for serie in exercice.series.all() if serie.est_reussie)
        total_series = exercice.series.count()

        if total_series > 0:
            taux_seance = (series_reussies / total_series) * 100

            # Mettre à jour le taux de réussite global (moyenne pondérée)
            ancien_taux = progression.taux_reussite
            nb_seances = progression.nombre_seances_machine

            if nb_seances == 0:
                progression.taux_reussite = taux_seance
            else:
                # Moyenne pondérée donnant plus d'importance aux sessions récentes
                poids_nouvelle_seance = min(0.3, 1.0 / (nb_seances + 1))
                progression.taux_reussite = (
                    ancien_taux * (1 - poids_nouvelle_seance) +
                    taux_seance * poids_nouvelle_seance
                )

        # Mettre à jour les autres champs
        progression.nombre_seances_machine += 1
        progression.derniere_seance = exercice.seance

        if exercice.charge_maximale_theorique:
            progression.dernier_1rm = exercice.charge_maximale_theorique

        # Vérifier si on doit progresser en poids
        if progression.evaluer_progression(exercice):
            success, ancien_poids, nouveau_poids = progression.progresser_poids()
            if success:
                progression.derniere_progression = timezone.now()

        progression.save()