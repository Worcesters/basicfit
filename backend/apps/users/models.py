"""
Modèles utilisateurs pour BasicFit
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour BasicFit
    """
    OBJECTIFS_SPORTIFS = [
        ('PRISE_MASSE', 'Prise de masse'),
        ('SECHE', 'Sèche'),
        ('FORCE', 'Force'),
        ('ENDURANCE', 'Endurance'),
        ('REMISE_FORME', 'Remise en forme'),
        ('PERFORMANCE', 'Performance'),
    ]

    NIVEAUX_EXPERIENCE = [
        ('DEBUTANT', 'Débutant'),
        ('INTERMEDIAIRE', 'Intermédiaire'),
        ('AVANCE', 'Avancé'),
        ('EXPERT', 'Expert'),
    ]

    # Champs personnalisés
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )
    prenom = models.CharField(
        max_length=30,
        verbose_name="Prénom"
    )
    nom = models.CharField(
        max_length=30,
        verbose_name="Nom"
    )
    telephone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
        )],
        verbose_name="Téléphone"
    )
    date_naissance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    poids = models.FloatField(
        null=True,
        blank=True,
        help_text="Poids en kg",
        verbose_name="Poids (kg)"
    )
    taille = models.FloatField(
        null=True,
        blank=True,
        help_text="Taille en cm",
        verbose_name="Taille (cm)"
    )
    objectif_sportif = models.CharField(
        max_length=20,
        choices=OBJECTIFS_SPORTIFS,
        default='REMISE_FORME',
        verbose_name="Objectif sportif"
    )
    niveau_experience = models.CharField(
        max_length=15,
        choices=NIVEAUX_EXPERIENCE,
        default='DEBUTANT',
        verbose_name="Niveau d'expérience"
    )
    mode_entrainement_prefere = models.ForeignKey(
        'core.ModeEntrainement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Mode d'entraînement préféré"
    )
    photo_profil = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )
    est_premium = models.BooleanField(
        default=False,
        verbose_name="Compte premium"
    )
    date_inscription_salle = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'inscription en salle"
    )
    salle_frequentee = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Salle fréquentée"
    )

    # Champs pour notifications
    notifications_actives = models.BooleanField(
        default=True,
        verbose_name="Notifications actives"
    )
    notification_rappel_entrainement = models.BooleanField(
        default=True,
        verbose_name="Rappel d'entraînement"
    )
    notification_progression = models.BooleanField(
        default=True,
        verbose_name="Notification de progression"
    )

    # Champs de suivi
    derniere_connexion_app = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière connexion"
    )
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['prenom', 'nom']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    @property
    def nom_complet(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.prenom} {self.nom}".strip()

    @property
    def imc(self):
        """Calcule l'IMC si poids et taille sont disponibles"""
        if self.poids and self.taille:
            taille_m = self.taille / 100  # Conversion cm -> m
            return round(self.poids / (taille_m ** 2), 2)
        return None

    @property
    def age(self):
        """Calcule l'âge de l'utilisateur"""
        if self.date_naissance:
            from datetime import date
            today = date.today()
            return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
        return None

    def save(self, *args, **kwargs):
        """Override save pour normaliser les données"""
        if self.prenom:
            self.prenom = self.prenom.strip().title()
        if self.nom:
            self.nom = self.nom.strip().upper()
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)


class ProfilUtilisateur(TimeStampedModel):
    """
    Modèle pour étendre les informations du profil utilisateur
    """
    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name="Utilisateur"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biographie"
    )
    objectifs_personnels = models.TextField(
        blank=True,
        verbose_name="Objectifs personnels"
    )
    blessures_actuelles = models.TextField(
        blank=True,
        verbose_name="Blessures ou limitations actuelles"
    )
    medicaments = models.TextField(
        blank=True,
        verbose_name="Médicaments"
    )
    frequence_entrainement_semaine = models.PositiveIntegerField(
        default=3,
        verbose_name="Fréquence d'entraînement par semaine"
    )
    duree_entrainement_moyenne = models.PositiveIntegerField(
        default=60,
        help_text="Durée en minutes",
        verbose_name="Durée moyenne d'entraînement (min)"
    )
    est_public = models.BooleanField(
        default=False,
        verbose_name="Profil public"
    )

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.utilisateur.nom_complet}"