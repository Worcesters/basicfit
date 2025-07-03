"""
Modèles de base et utilitaires communs pour BasicFit
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute created_at et updated_at à tous les modèles
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """Manager pour filtrer automatiquement les objets actifs"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeletableModel(TimeStampedModel):
    """
    Modèle abstrait qui permet la suppression douce (soft delete)
    """
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de suppression")

    objects = models.Manager()  # Manager par défaut
    active_objects = ActiveManager()  # Manager pour les objets actifs

    class Meta:
        abstract = True

    def soft_delete(self):
        """Suppression douce de l'objet"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restauration d'un objet supprimé"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class ModeEntrainement(TimeStampedModel):
    """
    Modèles pour les différents modes d'entraînement
    """
    TYPES_ENTRAINEMENT = [
        ('FORCE', 'Force'),
        ('PRISE_MASSE', 'Prise de masse'),
        ('SECHE', 'Sèche'),
        ('ENDURANCE', 'Endurance'),
        ('POWERLIFTING', 'Powerlifting'),
    ]

    nom = models.CharField(
        max_length=50,
        choices=TYPES_ENTRAINEMENT,
        unique=True,
        verbose_name="Nom du mode"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    series_recommandees = models.PositiveIntegerField(
        default=3,
        verbose_name="Nombre de séries recommandées"
    )
    repetitions_min = models.PositiveIntegerField(
        default=1,
        verbose_name="Répétitions minimum"
    )
    repetitions_max = models.PositiveIntegerField(
        default=15,
        verbose_name="Répétitions maximum"
    )
    repos_entre_series = models.PositiveIntegerField(
        default=90,
        help_text="Temps de repos en secondes",
        verbose_name="Repos entre séries (s)"
    )
    pourcentage_1rm_min = models.FloatField(
        default=0.6,
        verbose_name="% 1RM minimum"
    )
    pourcentage_1rm_max = models.FloatField(
        default=0.9,
        verbose_name="% 1RM maximum"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Mode d'entraînement"
        verbose_name_plural = "Modes d'entraînement"
        ordering = ['nom']

    def __str__(self):
        return self.get_nom_display()

    @property
    def repetitions_recommandees(self):
        """Calcule les répétitions recommandées selon le mode"""
        if self.nom == 'FORCE':
            return 5
        elif self.nom == 'PRISE_MASSE':
            return 12
        elif self.nom == 'SECHE':
            return 15
        elif self.nom == 'ENDURANCE':
            return 20
        elif self.nom == 'POWERLIFTING':
            return 3
        return 10