"""
Modèles simplifiés pour les sessions d'entraînement
Uniquement l'essentiel avec logging complet
"""
from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class SessionSimple(models.Model):
    """Session d'entraînement simplifiée"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_simple')
    nom = models.CharField(max_length=200, default="Entraînement")
    date = models.DateTimeField()
    duree = models.IntegerField(help_text="Durée en minutes")
    note_ressenti = models.IntegerField(default=5, help_text="Note de ressenti sur 10")
    commentaire = models.TextField(blank=True, default="")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bf_sessions_rapides'
        app_label = 'sessions_simple'
        ordering = ['-date']
        verbose_name = "Session Simple"
        verbose_name_plural = "Sessions Simples"
    
    def __str__(self):
        return f"{self.nom} - {self.date.strftime('%Y-%m-%d')} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        logger.info(f"💾 SAUVEGARDE SESSION - User: {self.user.id}, Nom: {self.nom}, Date: {self.date}")
        super().save(*args, **kwargs)
        logger.info(f"✅ SESSION SAUVEGARDÉE - ID: {self.id}")

class ExerciceSimple(models.Model):
    """Exercice dans une session"""
    session = models.ForeignKey(SessionSimple, on_delete=models.CASCADE, related_name='exercices')
    nom = models.CharField(max_length=200)
    series = models.IntegerField()
    reps = models.IntegerField()
    poids = models.FloatField(help_text="Poids en kg")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bf_exercices_rapides'
        app_label = 'sessions_simple'
        verbose_name = "Exercice Simple"
        verbose_name_plural = "Exercices Simples"
    
    def __str__(self):
        return f"{self.nom} - {self.series}x{self.reps}@{self.poids}kg"
    
    def save(self, *args, **kwargs):
        logger.info(f"💪 SAUVEGARDE EXERCICE - Session: {self.session.id}, Nom: {self.nom}, {self.series}x{self.reps}@{self.poids}kg")
        super().save(*args, **kwargs)
        logger.info(f"✅ EXERCICE SAUVEGARDÉ - ID: {self.id}")

class ImportCSVLog(models.Model):
    """Log des imports CSV pour traçabilité"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255, default="import.csv")
    total_lines = models.IntegerField(default=0)
    imported_count = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    errors_detail = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bf_logs_import_csv'
        app_label = 'sessions_simple'
        ordering = ['-created_at']
        verbose_name = "Log Import CSV"
        verbose_name_plural = "Logs Import CSV"
    
    def __str__(self):
        return f"Import {self.user.email} - {self.imported_count}/{self.total_lines} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"