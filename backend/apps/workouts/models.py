"""
Modèles pour les séances d'entraînement et la progression dans BasicFit
"""
import math
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.users.models import User
from apps.machines.models import Machine, VarianteMachine
from apps.core.models import ModeEntrainement


class SeanceEntrainement(TimeStampedModel):
    """
    Modèle pour une séance d'entraînement complète
    """
    STATUTS_SEANCE = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
        ('SUSPENDUE', 'Suspendue'),
    ]

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seances',
        verbose_name="Utilisateur"
    )
    mode_entrainement = models.ForeignKey(
        ModeEntrainement,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Mode d'entraînement"
    )
    nom = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom de la séance"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    # Dates et durées
    date_prevue = models.DateTimeField(
        verbose_name="Date prévue"
    )
    date_debut = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de début"
    )
    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    duree_prevue = models.PositiveIntegerField(
        default=60,
        help_text="Durée prévue en minutes",
        verbose_name="Durée prévue (min)"
    )

    # Statut et métriques
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_SEANCE,
        default='PLANIFIEE',
        verbose_name="Statut"
    )
    note_ressenti = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note de ressenti de 1 à 10",
        verbose_name="Note de ressenti"
    )
    note_difficulte = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note de difficulté de 1 à 10",
        verbose_name="Note de difficulté"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    # Métriques physiques
    poids_utilisateur = models.FloatField(
        null=True,
        blank=True,
        help_text="Poids au moment de la séance en kg",
        verbose_name="Poids (kg)"
    )
    frequence_cardiaque_repos = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque au repos",
        verbose_name="FC repos (bpm)"
    )
    frequence_cardiaque_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque maximale atteinte",
        verbose_name="FC max (bpm)"
    )

    # Données calculées
    volume_total = models.FloatField(
        default=0.0,
        help_text="Volume total de la séance (poids × reps × séries)",
        verbose_name="Volume total"
    )
    tonnage_total = models.FloatField(
        default=0.0,
        help_text="Tonnage total soulevé en kg",
        verbose_name="Tonnage total (kg)"
    )
    nombre_exercices = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre d'exercices"
    )
    nombre_series_totales = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de séries totales"
    )

    # Métadonnées
    salle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Salle"
    )
    partenaire_entrainement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Partenaire d'entraînement"
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Température en degrés Celsius",
        verbose_name="Température (°C)"
    )

    class Meta:
        verbose_name = "Séance d'entraînement"
        verbose_name_plural = "Séances d'entraînement"
        ordering = ['-date_prevue']
        indexes = [
            models.Index(fields=['utilisateur', 'date_prevue']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        if self.nom:
            return f"{self.nom} - {self.date_prevue.strftime('%d/%m/%Y')}"
        return f"Séance du {self.date_prevue.strftime('%d/%m/%Y')}"

    @property
    def duree_reelle(self):
        """Calcule la durée réelle de la séance en minutes"""
        if self.date_debut and self.date_fin:
            delta = self.date_fin - self.date_debut
            return int(delta.total_seconds() / 60)
        return None

    @property
    def est_terminee(self):
        """Vérifie si la séance est terminée"""
        return self.statut == 'TERMINEE'

    def commencer_seance(self):
        """Démarre la séance"""
        self.date_debut = timezone.now()
        self.statut = 'EN_COURS'
        self.save(update_fields=['date_debut', 'statut'])

    def terminer_seance(self):
        """Termine la séance et calcule les métriques"""
        self.date_fin = timezone.now()
        self.statut = 'TERMINEE'
        self.calculer_metriques()
        self.save()

    def calculer_metriques(self):
        """Calcule les métriques de la séance"""
        exercices = self.exercices.all()

        self.nombre_exercices = exercices.count()
        self.nombre_series_totales = sum(ex.nombre_series for ex in exercices)
        self.volume_total = sum(ex.volume_total for ex in exercices)
        self.tonnage_total = sum(ex.tonnage_total for ex in exercices)


class ExerciceSeance(TimeStampedModel):
    """
    Modèle pour un exercice dans une séance
    """
    STATUTS_EXERCICE = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ECHOUE', 'Échoué'),
        ('ABANDONNE', 'Abandonné'),
    ]

    seance = models.ForeignKey(
        SeanceEntrainement,
        on_delete=models.CASCADE,
        related_name='exercices',
        verbose_name="Séance"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    variante = models.ForeignKey(
        VarianteMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Variante"
    )

    # Configuration de l'exercice
    ordre_dans_seance = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre dans la séance"
    )
    series_prevues = models.PositiveIntegerField(
        default=3,
        verbose_name="Séries prévues"
    )
    repetitions_prevues = models.PositiveIntegerField(
        default=10,
        verbose_name="Répétitions prévues"
    )
    duree_prevue = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée prévue en secondes (pour exercices de durée)",
        verbose_name="Durée prévue (s)"
    )
    poids_prevu = models.FloatField(
        help_text="Poids prévu en kg",
        verbose_name="Poids prévu (kg)"
    )
    repos_prevu = models.PositiveIntegerField(
        default=90,
        help_text="Repos prévu entre séries en secondes",
        verbose_name="Repos prévu (s)"
    )

    # Résultats
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_EXERCICE,
        default='PLANIFIE',
        verbose_name="Statut"
    )
    nombre_series = models.PositiveIntegerField(
        default=0,
        verbose_name="Séries réalisées"
    )
    repetitions_realisees = models.PositiveIntegerField(
        default=0,
        verbose_name="Répétitions totales réalisées"
    )
    duree_realisee = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée réalisée en secondes (pour exercices de durée)",
        verbose_name="Durée réalisée (s)"
    )
    poids_utilise = models.FloatField(
        null=True,
        blank=True,
        help_text="Poids réellement utilisé en kg",
        verbose_name="Poids utilisé (kg)"
    )
    repos_reel = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Repos réel en secondes",
        verbose_name="Repos réel (s)"
    )

    # Métriques calculées
    volume_total = models.FloatField(
        default=0.0,
        help_text="Volume total (poids × reps × séries)",
        verbose_name="Volume total"
    )
    tonnage_total = models.FloatField(
        default=0.0,
        help_text="Tonnage total soulevé",
        verbose_name="Tonnage total"
    )
    charge_maximale_theorique = models.FloatField(
        null=True,
        blank=True,
        help_text="1RM estimé avec formule de Brzycki",
        verbose_name="1RM estimé (kg)"
    )

    # Temps et ressenti
    duree_totale = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée totale de l'exercice en secondes",
        verbose_name="Durée totale (s)"
    )
    note_ressenti = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Note de ressenti"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Exercice de séance"
        verbose_name_plural = "Exercices de séances"
        ordering = ['seance', 'ordre_dans_seance']
        unique_together = ['seance', 'ordre_dans_seance']

    def __str__(self):
        variante = f" ({self.variante.nom})" if self.variante else ""
        return f"{self.machine.nom}{variante} - {self.seance}"

    def calculer_1rm_brzycki(self, poids=None, repetitions=None):
        """
        Calcule le 1RM estimé avec la formule de Brzycki
        1RM ≈ Poids × (36 / (37 - reps))
        """
        if poids is None:
            poids = self.poids_utilise
        if repetitions is None:
            # Prendre les répétitions moyennes par série
            if self.nombre_series > 0:
                repetitions = self.repetitions_realisees / self.nombre_series
            else:
                repetitions = self.repetitions_prevues

        if poids and repetitions and repetitions < 37:
            return round(poids * (36 / (37 - repetitions)), 2)
        return None

    def calculer_metriques(self):
        """Calcule toutes les métriques de l'exercice"""
        if self.poids_utilise and self.repetitions_realisees:
            self.tonnage_total = self.poids_utilise * self.repetitions_realisees
            self.volume_total = self.tonnage_total * self.nombre_series

            # Calcul du 1RM si on a les données
            if self.nombre_series > 0:
                reps_moyenne = self.repetitions_realisees / self.nombre_series
                self.charge_maximale_theorique = self.calculer_1rm_brzycki(
                    self.poids_utilise, reps_moyenne
                )

    def save(self, *args, **kwargs):
        """Override save pour calculer les métriques automatiquement"""
        self.calculer_metriques()
        super().save(*args, **kwargs)


class SeriExercice(TimeStampedModel):
    """
    Modèle pour une série d'un exercice
    """
    STATUTS_SERIE = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('REUSSIE', 'Réussie'),
        ('ECHOUEE', 'Échouée'),
        ('PARTIELLE', 'Partielle'),
    ]

    exercice = models.ForeignKey(
        ExerciceSeance,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name="Exercice"
    )
    numero_serie = models.PositiveIntegerField(
        verbose_name="Numéro de série"
    )

    # Prévisions
    repetitions_prevues = models.PositiveIntegerField(
        verbose_name="Répétitions prévues"
    )
    duree_prevue = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée prévue en secondes (pour exercices de durée)",
        verbose_name="Durée prévue (s)"
    )
    poids_prevu = models.FloatField(
        verbose_name="Poids prévu (kg)"
    )
    repos_prevu = models.PositiveIntegerField(
        default=90,
        help_text="Repos après cette série en secondes",
        verbose_name="Repos prévu (s)"
    )

    # Résultats
    repetitions_realisees = models.PositiveIntegerField(
        default=0,
        verbose_name="Répétitions réalisées"
    )
    duree_realisee = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée réalisée en secondes (pour exercices de durée)",
        verbose_name="Durée réalisée (s)"
    )
    poids_utilise = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Poids utilisé (kg)"
    )

    # Métriques
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_SERIE,
        default='PLANIFIEE',
        verbose_name="Statut"
    )
    duree_serie = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée de la série en secondes",
        verbose_name="Durée série (s)"
    )
    frequence_cardiaque_apres = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque après la série",
        verbose_name="FC après série (bpm)"
    )
    note_effort = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note d'effort perçu (RPE)",
        verbose_name="Note d'effort"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Série d'exercice"
        verbose_name_plural = "Séries d'exercices"
        ordering = ['exercice', 'numero_serie']
        unique_together = ['exercice', 'numero_serie']

    def __str__(self):
        return f"Série {self.numero_serie} - {self.exercice}"

    @property
    def est_reussie(self):
        """Vérifie si la série est réussie (toutes les reps prévues)"""
        return self.repetitions_realisees >= self.repetitions_prevues

    @property
    def pourcentage_reussite(self):
        """Calcule le pourcentage de réussite de la série"""
        if self.repetitions_prevues > 0:
            return min(100, (self.repetitions_realisees / self.repetitions_prevues) * 100)
        return 0


class ProgressionMachine(TimeStampedModel):
    """
    Modèle pour suivre la progression sur une machine
    """
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progressions',
        verbose_name="Utilisateur"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    mode_entrainement = models.ForeignKey(
        ModeEntrainement,
        on_delete=models.CASCADE,
        verbose_name="Mode d'entraînement"
    )

    # Progression actuelle
    poids_actuel = models.FloatField(
        verbose_name="Poids actuel (kg)"
    )
    series_actuelles = models.PositiveIntegerField(
        default=3,
        verbose_name="Séries actuelles"
    )
    repetitions_actuelles = models.PositiveIntegerField(
        default=10,
        verbose_name="Répétitions actuelles"
    )

    # Dernière performance
    derniere_seance = models.ForeignKey(
        SeanceEntrainement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progressions_mises_a_jour',
        verbose_name="Dernière séance"
    )
    dernier_1rm = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Dernier 1RM (kg)"
    )

    # Métriques de progression
    nombre_seances_machine = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de séances sur cette machine"
    )
    progression_poids_total = models.FloatField(
        default=0.0,
        help_text="Progression totale en kg depuis le début",
        verbose_name="Progression poids total (kg)"
    )
    taux_reussite = models.FloatField(
        default=0.0,
        help_text="Taux de réussite en pourcentage",
        verbose_name="Taux de réussite (%)"
    )

    # Configuration de progression
    increment_automatique = models.BooleanField(
        default=True,
        verbose_name="Incrément automatique"
    )
    seuil_progression = models.FloatField(
        default=90.0,
        help_text="Seuil de réussite pour progression automatique (%)",
        verbose_name="Seuil de progression (%)"
    )

    # Dates importantes
    premiere_utilisation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Première utilisation"
    )
    derniere_progression = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière progression"
    )

    class Meta:
        verbose_name = "Progression sur machine"
        verbose_name_plural = "Progressions sur machines"
        unique_together = ['utilisateur', 'machine', 'mode_entrainement']
        ordering = ['utilisateur', 'machine']

    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.machine.nom} ({self.mode_entrainement})"

    def evaluer_progression(self, exercice_seance):
        """
        Évalue s'il faut progresser en poids basé sur la performance
        """
        if not self.increment_automatique:
            return False

        # Si pas d'exercice_seance fourni, utiliser l'historique
        if exercice_seance is None:
            return self.evaluer_progression_historique()

        # Calculer le taux de réussite de cette séance
        series_reussies = 0
        for serie in exercice_seance.series.all():
            if serie.est_reussie:
                series_reussies += 1

        if exercice_seance.nombre_series > 0:
            taux_reussite_seance = (series_reussies / exercice_seance.nombre_series) * 100
        else:
            return False

        # Si le taux de réussite dépasse le seuil, on peut progresser
        if taux_reussite_seance >= self.seuil_progression:
            return True

        return False

    def evaluer_progression_historique(self):
        """
        Évalue la progression basée sur l'historique des séances
        """
        if not self.increment_automatique:
            return False

        # Utiliser le taux de réussite global de la progression
        if self.taux_reussite >= self.seuil_progression:
            return True

        return False

    def progresser_poids(self):
        """Augmente le poids selon l'incrément de la machine"""
        increment = self.machine.increment_poids
        nouveau_poids = self.poids_actuel + increment

        if nouveau_poids <= self.machine.poids_maximum:
            ancien_poids = self.poids_actuel
            self.poids_actuel = nouveau_poids
            self.progression_poids_total += increment
            self.derniere_progression = timezone.now()
            self.save()

            return True, ancien_poids, nouveau_poids

        return False, self.poids_actuel, self.poids_actuel

    def recommander_prochaine_seance(self):
        """
        Recommande les paramètres pour la prochaine séance
        """
        series = self.mode_entrainement.series_recommandees
        repetitions = self.mode_entrainement.repetitions_recommandees

        return {
            'poids': self.poids_actuel,
            'series': series,
            'repetitions': repetitions,
            'repos': self.mode_entrainement.repos_entre_series,
        }

    def calculer_recommandation_professionnelle(self):
        """
        Système de recommandation professionnel basé sur :
        1. Type de profil (prise de masse, sèche, maintenir)
        2. Type d'entraînement (endurance, volume, puissance)
        3. 1RM calculé à partir des séances précédentes
        4. Taux de réussite adaptatif
        """
        from django.utils import timezone
        from datetime import timedelta

        # Récupérer les données utilisateur et mode d'entraînement
        user = self.utilisateur
        mode = self.mode_entrainement

        # 1. ANALYSE DU PROFIL UTILISATEUR
        objectif = user.objectif_sportif
        niveau = user.niveau_experience

        # 2. ANALYSE DU MODE D'ENTRAÎNEMENT
        type_entrainement = mode.nom if mode else 'PRISE_MASSE'

        # 3. CALCULER LE 1RM ACTUEL À PARTIR DES SÉANCES RÉCENTES
        unrm_actuel = self._calculer_1rm_recent()

        # 4. ANALYSER LES PERFORMANCES RÉCENTES
        performances_recentes = self._analyser_performances_recentes()

        # 5. CALCULER LA RECOMMANDATION BASÉE SUR LA LOGIQUE COACH
        recommandation = self._calculer_recommandation_coach(
            objectif, type_entrainement, unrm_actuel, performances_recentes
        )

        return recommandation

    def _calculer_1rm_recent(self):
        """
        Calcule le 1RM basé sur les 5 dernières séances avec cette machine
        """
        # Récupérer les 5 dernières séances TERMINÉES de cet utilisateur avec cette machine
        seances_recentes = SeanceEntrainement.objects.filter(
            utilisateur=self.utilisateur,
            statut='TERMINEE',
            exercices__machine=self.machine
        ).distinct().order_by('-date_fin')[:5]

        meilleur_1rm = 0.0
        meilleur_performance = 0.0

        for seance in seances_recentes:
            exercice = seance.exercices.filter(machine=self.machine).first()
            if exercice:
                # Calculer 1RM pour cette séance si pas déjà fait
                if not exercice.charge_maximale_theorique and exercice.poids_utilise and exercice.repetitions_realisees:
                    exercice.calculer_metriques()
                    exercice.save()
                
                # Prendre le meilleur 1RM
                if exercice.charge_maximale_theorique:
                    meilleur_1rm = max(meilleur_1rm, exercice.charge_maximale_theorique)
                
                # Aussi considérer le poids max utilisé comme référence
                if exercice.poids_utilise:
                    meilleur_performance = max(meilleur_performance, exercice.poids_utilise)

        # Utiliser le meilleur 1RM calculé, sinon le 1RM stocké, sinon une estimation basée sur le poids max
        if meilleur_1rm > 0:
            return meilleur_1rm
        elif self.dernier_1rm and self.dernier_1rm > 0:
            return self.dernier_1rm
        elif meilleur_performance > 0:
            # Estimation conservative: poids max utilisé + 20% (approximation pour 1RM)
            return meilleur_performance * 1.2
        else:
            # Dernier recours: utiliser le poids actuel comme base
            return self.poids_actuel * 1.1 if self.poids_actuel > 0 else 20.0

    def _analyser_performances_recentes(self):
        """
        Analyse les performances des 2 dernières séances
        """
        # Récupérer les 2 dernières séances TERMINÉES de cet utilisateur
        seances_recentes = SeanceEntrainement.objects.filter(
            utilisateur=self.utilisateur,
            statut='TERMINEE'
        ).order_by('-date_fin')[:2]

        if not seances_recentes:
            return {
                'taux_reussite': 0.0,
                'series_reussies': 0,
                'series_totales': 0,
                'poids_utilise': self.poids_actuel,
                'repetitions_moyennes': 10
            }

        # Analyser la dernière séance qui contient cet exercice
        for seance in seances_recentes:
            exercice = seance.exercices.filter(machine=self.machine).first()
            if exercice:
                # Compter les séries réussies
                series_reussies = 0
                series_totales = 0
                repetitions_total = 0

                for serie in exercice.series.all():
                    series_totales += 1
                    repetitions_total += serie.repetitions_realisees

                    # Une série est réussie si elle atteint au moins 80% des reps prévues
                    if serie.repetitions_realisees >= serie.repetitions_prevues * 0.8:
                        series_reussies += 1

                taux_reussite = (series_reussies / series_totales * 100) if series_totales > 0 else 0
                repetitions_moyennes = repetitions_total / series_totales if series_totales > 0 else 10

                return {
                    'taux_reussite': taux_reussite,
                    'series_reussies': series_reussies,
                    'series_totales': series_totales,
                    'poids_utilise': exercice.poids_utilise or self.poids_actuel,
                    'repetitions_moyennes': repetitions_moyennes
                }

        # Si aucune séance ne contient cet exercice
        return {
            'taux_reussite': 0.0,
            'series_reussies': 0,
            'series_totales': 0,
            'poids_utilise': self.poids_actuel,
            'repetitions_moyennes': 10
        }

    def _calculer_recommandation_coach(self, objectif, type_entrainement, unrm_actuel, performances):
        """
        Logique de recommandation intelligente basée sur l'expertise coach et le 1RM
        """
        poids_actuel = self.poids_actuel
        increment = self.machine.increment_poids
        taux_reussite = performances['taux_reussite']
        repetitions_moyennes = performances['repetitions_moyennes']

        # DÉFINIR LES OBJECTIFS PAR TYPE D'ENTRAÎNEMENT
        objectifs_reps = {
            'FORCE': {'min': 1, 'max': 5, 'cible': 3, 'pct_1rm': 0.85},
            'PRISE_MASSE': {'min': 8, 'max': 12, 'cible': 10, 'pct_1rm': 0.70},
            'SECHE': {'min': 12, 'max': 15, 'cible': 12, 'pct_1rm': 0.65},
            'ENDURANCE': {'min': 15, 'max': 20, 'cible': 15, 'pct_1rm': 0.60},
            'POWERLIFTING': {'min': 1, 'max': 3, 'cible': 2, 'pct_1rm': 0.90}
        }

        # Récupérer les objectifs pour ce type d'entraînement
        objectif_reps = objectifs_reps.get(type_entrainement, objectifs_reps['PRISE_MASSE'])
        reps_cible = objectif_reps['cible']
        reps_min = objectif_reps['min']
        reps_max = objectif_reps['max']
        pct_1rm_cible = objectif_reps['pct_1rm']

        # CALCUL BASÉ SUR LE 1RM SI DISPONIBLE
        if unrm_actuel > 0:
            poids_theorique = unrm_actuel * pct_1rm_cible
            
            # Arrondir au multiple de l'incrément le plus proche
            poids_theorique = round(poids_theorique / increment) * increment
            
            # S'assurer que c'est dans les limites de la machine
            poids_theorique = max(self.machine.poids_minimum, 
                                min(poids_theorique, self.machine.poids_maximum))
            
            # LOGIQUE DE PROGRESSION INTELLIGENTE BASÉE SUR LE 1RM
            
            # Si pas de données de performance récentes, utiliser le calcul théorique
            if taux_reussite == 0 and performances['series_totales'] == 0:
                return poids_theorique
            
            # Cas 1: TAUX DE RÉUSSITE EXCELLENT (> 90%)
            if taux_reussite >= 90:
                # Progression vers le poids théorique ou légèrement au-dessus
                if poids_actuel < poids_theorique:
                    nouveau_poids = min(poids_actuel + increment, poids_theorique)
                else:
                    nouveau_poids = min(poids_actuel + increment, self.machine.poids_maximum)
                return nouveau_poids
            
            # Cas 2: TAUX DE RÉUSSITE BON (75-90%)
            elif taux_reussite >= 75:
                # Progression modérée vers le poids théorique
                if poids_actuel < poids_theorique * 0.95:  # Si on est en dessous de 95% du théorique
                    return min(poids_actuel + increment, poids_theorique)
                else:
                    return poids_actuel
            
            # Cas 3: TAUX DE RÉUSSITE MOYEN (60-75%)
            elif taux_reussite >= 60:
                # Maintenir ou réduire légèrement si trop lourd
                if poids_actuel > poids_theorique:
                    return max(poids_theorique, poids_actuel - increment)
                else:
                    return poids_actuel
            
            # Cas 4: TAUX DE RÉUSSITE FAIBLE (< 60%)
            else:
                # Retour vers un poids plus gérable basé sur le 1RM
                poids_reduit = poids_theorique * 0.85  # Réduire à 85% du poids théorique
                poids_reduit = round(poids_reduit / increment) * increment
                return max(self.machine.poids_minimum, poids_reduit)
        
        # FALLBACK: LOGIQUE TRADITIONNELLE SI PAS DE 1RM FIABLE
        else:
            # Utiliser la logique basée sur les performances seulement
            if taux_reussite >= 90:
                nouveau_poids = min(poids_actuel + increment, self.machine.poids_maximum)
                return nouveau_poids
            elif taux_reussite >= 80:
                if reps_min <= repetitions_moyennes <= reps_max:
                    nouveau_poids = min(poids_actuel + increment, self.machine.poids_maximum)
                    return nouveau_poids
                else:
                    return poids_actuel
            elif taux_reussite >= 60:
                return poids_actuel
            else:
                reduction = increment * 2
                nouveau_poids = max(poids_actuel - reduction, self.machine.poids_minimum)
                return nouveau_poids

        # Ultime fallback - ne devrait jamais arriver
        return max(poids_actuel, self.machine.poids_minimum)

    def calculer_recommandation_intelligente(self):
        """
        Alias pour la nouvelle méthode professionnelle
        """
        return self.calculer_recommandation_professionnelle()

    def detecter_stagnation(self):
        """
        Détecte si l'utilisateur stagne depuis trop longtemps au même poids
        """
        # Si pas de progression depuis plus de 2 semaines et taux de réussite > 70%
        if self.derniere_progression:
            from django.utils import timezone
            from datetime import timedelta

            deux_semaines = timedelta(weeks=2)
            if (timezone.now() - self.derniere_progression) > deux_semaines:
                if self.taux_reussite >= 70.0:  # Seuil plus bas pour forcer la progression
                    return True

        # Si jamais de progression et taux de réussite élevé
        elif self.taux_reussite >= 80.0 and self.nombre_seances_machine >= 3:
            return True

        return False