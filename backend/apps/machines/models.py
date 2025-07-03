"""
Modèles pour les machines et équipements de BasicFit
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import TimeStampedModel, SoftDeletableModel


class GroupeMusculaire(TimeStampedModel):
    """
    Modèle pour les groupes musculaires
    """
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du groupe musculaire"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    couleur = models.CharField(
        max_length=7,
        default="#3498db",
        help_text="Code couleur hexadécimal (ex: #3498db)",
        verbose_name="Couleur"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nom de l'icône (Material Icons ou Font Awesome)",
        verbose_name="Icône"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Groupe musculaire"
        verbose_name_plural = "Groupes musculaires"
        ordering = ['ordre_affichage', 'nom']

    def __str__(self):
        return self.nom


class CategorieMachine(TimeStampedModel):
    """
    Modèle pour catégoriser les machines
    """
    TYPES_CATEGORIES = [
        ('CARDIO', 'Cardio'),
        ('MUSCULATION', 'Musculation'),
        ('FONCTIONNEL', 'Fonctionnel'),
        ('POIDS_LIBRE', 'Poids libre'),
        ('MACHINE_GUIDEE', 'Machine guidée'),
        ('CABLE', 'Câble'),
    ]

    nom = models.CharField(
        max_length=30,
        choices=TYPES_CATEGORIES,
        unique=True,
        verbose_name="Nom de la catégorie"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    couleur = models.CharField(
        max_length=7,
        default="#2ecc71",
        verbose_name="Couleur"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icône"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Catégorie de machine"
        verbose_name_plural = "Catégories de machines"
        ordering = ['nom']

    def __str__(self):
        return self.get_nom_display()


class Machine(SoftDeletableModel):
    """
    Modèle pour les machines et équipements
    """
    NIVEAUX_DIFFICULTE = [
        ('DEBUTANT', 'Débutant'),
        ('INTERMEDIAIRE', 'Intermédiaire'),
        ('AVANCE', 'Avancé'),
        ('EXPERT', 'Expert'),
    ]

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la machine"
    )
    nom_anglais = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom anglais"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    instructions = models.TextField(
        help_text="Instructions d'utilisation détaillées",
        verbose_name="Instructions d'utilisation"
    )

    # Catégorisation
    categorie = models.ForeignKey(
        CategorieMachine,
        on_delete=models.CASCADE,
        verbose_name="Catégorie"
    )
    groupes_musculaires_primaires = models.ManyToManyField(
        GroupeMusculaire,
        related_name='machines_primaires',
        verbose_name="Groupes musculaires primaires"
    )
    groupes_musculaires_secondaires = models.ManyToManyField(
        GroupeMusculaire,
        related_name='machines_secondaires',
        blank=True,
        verbose_name="Groupes musculaires secondaires"
    )

    # Caractéristiques techniques
    increment_poids = models.FloatField(
        default=2.5,
        validators=[MinValueValidator(0.5)],
        help_text="Incrément minimum de poids en kg",
        verbose_name="Incrément de poids (kg)"
    )
    poids_minimum = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0)],
        help_text="Poids minimum possible en kg",
        verbose_name="Poids minimum (kg)"
    )
    poids_maximum = models.FloatField(
        default=200.0,
        validators=[MinValueValidator(1)],
        help_text="Poids maximum possible en kg",
        verbose_name="Poids maximum (kg)"
    )

    # Métadonnées
    niveau_difficulte = models.CharField(
        max_length=15,
        choices=NIVEAUX_DIFFICULTE,
        default='DEBUTANT',
        verbose_name="Niveau de difficulté"
    )
    popularite = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Score de popularité (0-100)",
        verbose_name="Popularité"
    )
    est_disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible"
    )
    necessite_supervision = models.BooleanField(
        default=False,
        verbose_name="Nécessite supervision"
    )

    # Médias
    image_principale = models.ImageField(
        upload_to='machines/images/',
        blank=True,
        null=True,
        verbose_name="Image principale"
    )
    video_demonstration = models.URLField(
        blank=True,
        verbose_name="Vidéo de démonstration"
    )

    # Informations techniques
    fabricant = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Fabricant"
    )
    modele = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Modèle"
    )
    numero_serie = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numéro de série"
    )

    # Métadonnées pour l'affichage
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Tags séparés par des virgules",
        verbose_name="Tags"
    )

    # Statistiques
    nombre_utilisations = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre d'utilisations"
    )
    note_moyenne = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Note moyenne"
    )

    class Meta:
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        ordering = ['categorie', 'ordre_affichage', 'nom']
        indexes = [
            models.Index(fields=['categorie', 'est_disponible']),
            models.Index(fields=['popularite']),
        ]

    def __str__(self):
        return self.nom

    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError

        if self.poids_minimum >= self.poids_maximum:
            raise ValidationError("Le poids minimum doit être inférieur au poids maximum")

        if self.increment_poids > (self.poids_maximum - self.poids_minimum):
            raise ValidationError("L'incrément ne peut pas être supérieur à la plage de poids")

    @property
    def groupes_musculaires_tous(self):
        """Retourne tous les groupes musculaires (primaires + secondaires)"""
        primaires = list(self.groupes_musculaires_primaires.all())
        secondaires = list(self.groupes_musculaires_secondaires.all())
        return primaires + secondaires

    @property
    def tags_liste(self):
        """Retourne la liste des tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def incrementer_utilisation(self):
        """Incrémente le compteur d'utilisations"""
        self.nombre_utilisations += 1
        self.save(update_fields=['nombre_utilisations'])


class VarianteMachine(TimeStampedModel):
    """
    Modèle pour les variantes d'exercices sur une machine
    """
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name='variantes',
        verbose_name="Machine"
    )
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la variante"
    )
    description = models.TextField(
        verbose_name="Description de la variante"
    )
    niveau_difficulte = models.CharField(
        max_length=15,
        choices=Machine.NIVEAUX_DIFFICULTE,
        default='DEBUTANT',
        verbose_name="Niveau de difficulté"
    )
    groupes_musculaires_specifiques = models.ManyToManyField(
        GroupeMusculaire,
        blank=True,
        verbose_name="Groupes musculaires spécifiques à cette variante"
    )
    instructions_specifiques = models.TextField(
        blank=True,
        verbose_name="Instructions spécifiques"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Variante de machine"
        verbose_name_plural = "Variantes de machines"
        unique_together = ['machine', 'nom']

    def __str__(self):
        return f"{self.machine.nom} - {self.nom}"