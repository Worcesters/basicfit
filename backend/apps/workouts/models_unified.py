"""
Architecture unifiée pour BasicFit v2 - Table unique pour tous les exercices effectués
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.machines.models import Machine

class ExerciceEffectueUnifie(TimeStampedModel):
    """
    TABLE UNIQUE pour tous les exercices effectués dans l'application
    - Import CSV calendrier
    - Entraînements manuels temps réel  
    - Exercices individuels
    """
    
    SOURCES_EXERCICE = [
        ('CSV_IMPORT', 'Import CSV calendrier'),
        ('MANUEL_TEMPS_REEL', 'Entraînement manuel temps réel'),
        ('EXERCICE_INDIVIDUEL', 'Exercice individuel'),
        ('IMPORT_EXTERNE', 'Import externe (autre app)'),
    ]
    
    # Identification
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='exercices_effectues_unifies'
    )
    
    # Source et traçabilité
    source = models.CharField(
        max_length=30, 
        choices=SOURCES_EXERCICE,
        help_text="Origine de l'exercice"
    )
    
    # Informations temporelles
    date_exercice = models.DateTimeField(
        help_text="Date et heure de réalisation de l'exercice"
    )
    
    # Informations de la séance (optionnel)
    nom_seance = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Nom de la séance si applicable"
    )
    duree_seance_minutes = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Durée totale de la séance en minutes"
    )
    
    # Exercice
    nom_exercice = models.CharField(
        max_length=200,
        help_text="Nom de l'exercice effectué"
    )
    machine = models.ForeignKey(
        Machine, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Machine utilisée (si applicable)"
    )
    
    # Paramètres d'exécution
    series_effectuees = models.PositiveIntegerField(
        help_text="Nombre de séries réalisées"
    )
    repetitions_totales = models.PositiveIntegerField(
        help_text="Total des répétitions sur toutes les séries"
    )
    poids_utilise = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Poids utilisé (kg)"
    )
    
    # Métriques calculées
    volume_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Volume total (poids × répétitions)",
        editable=False
    )
    
    # Données d'import CSV (pour traçabilité)
    ligne_csv_originale = models.TextField(
        blank=True, 
        null=True,
        help_text="Ligne CSV originale (pour debug)"
    )
    
    # Performance et qualité
    taux_reussite = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100.00,
        help_text="Pourcentage de réussite de l'exercice"
    )
    
    temps_repos_seconde = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Temps de repos après l'exercice (secondes)"
    )
    
    # Notes et commentaires
    commentaire_utilisateur = models.TextField(
        blank=True, 
        null=True,
        help_text="Commentaire de l'utilisateur sur l'exercice"
    )
    
    class Meta:
        db_table = 'bf_exercices_effectues'
        verbose_name = 'Exercice effectué'
        verbose_name_plural = 'Exercices effectués'
        ordering = ['-date_exercice', 'nom_exercice']
        indexes = [
            models.Index(fields=['utilisateur', 'date_exercice']),
            models.Index(fields=['utilisateur', 'machine']),
            models.Index(fields=['utilisateur', 'nom_exercice']),
            models.Index(fields=['source', 'date_exercice']),
        ]
    
    def save(self, *args, **kwargs):
        # Calcul automatique du volume
        self.volume_total = float(self.poids_utilise) * float(self.repetitions_totales)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.nom_exercice} ({self.date_exercice.strftime('%d/%m/%Y')})"
    
    @property
    def repetitions_moyennes_par_serie(self):
        """Répétitions moyennes par série"""
        if self.series_effectuees > 0:
            return round(self.repetitions_totales / self.series_effectuees, 1)
        return 0
    
    @property
    def est_import_csv(self):
        """Vrai si l'exercice vient d'un import CSV"""
        return self.source == 'CSV_IMPORT'
    
    @property
    def est_manuel(self):
        """Vrai si l'exercice a été fait manuellement"""
        return self.source in ['MANUEL_TEMPS_REEL', 'EXERCICE_INDIVIDUEL']


class CalendrierEntrainementSimple(TimeStampedModel):
    """
    Métadonnées des séances d'entraînement (surtout pour les imports CSV)
    Les exercices individuels sont dans ExerciceEffectueUnifie
    """
    
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='calendrier_entrainements_simples'
    )
    
    date_entrainement = models.DateField()
    nom_seance = models.CharField(max_length=200)
    
    # Métriques globales de la séance
    duree_totale_minutes = models.PositiveIntegerField(
        help_text="Durée totale de la séance"
    )
    nombre_exercices = models.PositiveIntegerField(
        default=0,
        help_text="Nombre d'exercices dans cette séance"
    )
    volume_total_seance = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        help_text="Volume total de la séance"
    )
    
    # Traçabilité
    source_donnees = models.CharField(
        max_length=50, 
        choices=[
            ('CSV_IMPORT', 'Import CSV'),
            ('MANUEL', 'Séance manuelle'),
            ('PLANIFIE', 'Séance planifiée réalisée'),
        ],
        default='MANUEL'
    )
    
    commentaire = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'bf_calendrier_simple'
        verbose_name = 'Séance d\'entraînement'
        verbose_name_plural = 'Séances d\'entraînement'
        ordering = ['-date_entrainement']
        unique_together = ['utilisateur', 'date_entrainement', 'nom_seance']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.nom_seance} ({self.date_entrainement})"
    
    def mettre_a_jour_metriques(self):
        """Met à jour les métriques de la séance basées sur les exercices"""
        exercices = ExerciceEffectueUnifie.objects.filter(
            utilisateur=self.utilisateur,
            date_exercice__date=self.date_entrainement,
            nom_seance=self.nom_seance
        )
        
        self.nombre_exercices = exercices.count()
        self.volume_total_seance = sum(ex.volume_total for ex in exercices)
        self.save(update_fields=['nombre_exercices', 'volume_total_seance'])