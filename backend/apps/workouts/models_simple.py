"""
Modèle simple pour les séances calendrier - Version CSV
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.users.models import User


class SeanceSimple(TimeStampedModel):
    """
    Modèle simplifié pour les séances importées depuis CSV
    Format: machine,date,type
    """
    TYPES_EXERCICE = [
        ('CARDIO', 'Cardio'),
        ('MUSCULATION', 'Musculation'),
        ('FORCE', 'Force'),
        ('ENDURANCE', 'Endurance'),
        ('GAINAGE', 'Gainage'),
        ('AUTRE', 'Autre'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seances_simples',
        verbose_name="Utilisateur"
    )
    
    # Données depuis le CSV
    machine_nom = models.CharField(
        max_length=200,
        verbose_name="Nom de la machine"
    )
    
    date_seance = models.DateField(
        verbose_name="Date de la séance"
    )
    
    type_exercice = models.CharField(
        max_length=20,
        choices=TYPES_EXERCICE,
        default='AUTRE',
        verbose_name="Type d'exercice"
    )
    
    # Données optionnelles pour les détails
    duree_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Durée en minutes"
    )
    
    note_ressenti = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Note de ressenti (1-10)"
    )
    
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )
    
    class Meta:
        verbose_name = "Séance Simple"
        verbose_name_plural = "Séances Simples"
        ordering = ['-date_seance', 'machine_nom']
        indexes = [
            models.Index(fields=['utilisateur', 'date_seance']),
            models.Index(fields=['date_seance']),
        ]
    
    def __str__(self):
        return f"{self.machine_nom} - {self.date_seance.strftime('%d/%m/%Y')}"
    
    @classmethod
    def delete_all_for_user(cls, user):
        """Supprimer toutes les séances d'un utilisateur"""
        deleted_count = cls.objects.filter(utilisateur=user).count()
        cls.objects.filter(utilisateur=user).delete()
        return deleted_count
    
    @classmethod
    def import_from_csv_data(cls, user, csv_data):
        """
        Importer des données CSV
        Format attendu: [{'machine': str, 'date': str, 'type': str}, ...]
        """
        from datetime import datetime
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_data, 1):
            try:
                # Validation des colonnes requises
                if not all(key in row for key in ['machine', 'date', 'type']):
                    errors.append(f"Ligne {row_num}: Colonnes manquantes")
                    continue
                
                # Parse de la date
                date_str = row['date'].strip()
                try:
                    # Essayer différents formats de date
                    for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                        try:
                            date_obj = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                    else:
                        errors.append(f"Ligne {row_num}: Format de date invalide: {date_str}")
                        continue
                except Exception:
                    errors.append(f"Ligne {row_num}: Erreur parsing date: {date_str}")
                    continue
                
                # Normaliser le type d'exercice
                type_str = row['type'].strip().upper()
                type_mapping = {
                    'CARDIO': 'CARDIO',
                    'TAPIS': 'CARDIO',
                    'VELO': 'CARDIO',
                    'VÉLO': 'CARDIO',
                    'RAMEUR': 'CARDIO',
                    'ELLIPTIQUE': 'CARDIO',
                    'MUSCULATION': 'MUSCULATION',
                    'MUSCU': 'MUSCULATION',
                    'FORCE': 'FORCE',
                    'ENDURANCE': 'ENDURANCE',
                    'GAINAGE': 'GAINAGE',
                    'PLANK': 'GAINAGE',
                    'CORE': 'GAINAGE',
                }
                type_exercice = type_mapping.get(type_str, 'AUTRE')
                
                # Créer la séance (ou mettre à jour si elle existe)
                seance, created = cls.objects.get_or_create(
                    utilisateur=user,
                    machine_nom=row['machine'].strip(),
                    date_seance=date_obj,
                    defaults={
                        'type_exercice': type_exercice,
                        'duree_minutes': 60 if type_exercice == 'CARDIO' else 30,  # Durée par défaut
                    }
                )
                
                if created:
                    imported_count += 1
                
            except Exception as e:
                errors.append(f"Ligne {row_num}: Erreur: {str(e)}")
        
        return imported_count, errors