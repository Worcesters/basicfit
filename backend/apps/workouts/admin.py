"""
Configuration de l'admin Django pour les entraînements BasicFit v2
"""
from django.contrib import admin
from .models import (
    SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
)


@admin.register(SeanceEntrainement)
class SeanceEntrainementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'utilisateur', 'date_prevue', 'statut', 'volume_total']
    list_filter = ['statut', 'mode_entrainement', 'date_prevue']
    search_fields = ['nom', 'utilisateur__email']
    date_hierarchy = 'date_prevue'
    ordering = ['-date_prevue']


@admin.register(ExerciceSeance)
class ExerciceSeanceAdmin(admin.ModelAdmin):
    list_display = ['machine', 'seance', 'poids_utilise', 'nombre_series', 'statut']
    list_filter = ['statut', 'machine']
    search_fields = ['machine__nom', 'seance__nom']
    ordering = ['seance', 'ordre_dans_seance']


@admin.register(SeriExercice)
class SeriExerciceAdmin(admin.ModelAdmin):
    list_display = ['exercice', 'numero_serie', 'repetitions_realisees', 'poids_utilise', 'statut']
    list_filter = ['statut']
    ordering = ['exercice', 'numero_serie']


@admin.register(ProgressionMachine)
class ProgressionMachineAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'machine', 'poids_actuel', 'taux_reussite', 'nombre_seances_machine']
    list_filter = ['mode_entrainement', 'increment_automatique']
    search_fields = ['utilisateur__email', 'machine__nom']
    ordering = ['utilisateur', 'machine']


admin.site.site_header = "BasicFit v2 - Administration"
admin.site.site_title = "BasicFit Admin"
admin.site.index_title = "Gestion des Entraînements"