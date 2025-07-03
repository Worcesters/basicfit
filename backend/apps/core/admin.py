"""
Configuration de l'admin Django pour les modèles core BasicFit
"""
from django.contrib import admin
from .models import ModeEntrainement


@admin.register(ModeEntrainement)
class ModeEntrainementAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'get_nom_display', 'repetitions_min', 'repetitions_max',
        'pourcentage_1rm_min', 'pourcentage_1rm_max', 'is_active', 'created_at'
    ]
    list_filter = ['nom', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['nom', 'description']
    ordering = ['nom']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description')
        }),
        ('Paramètres d\'entraînement', {
            'fields': (
                'series_recommandees', 'repetitions_min', 'repetitions_max',
                'pourcentage_1rm_min', 'pourcentage_1rm_max'
            )
        }),
        ('Temps de repos', {
            'fields': ('repos_entre_series',)
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
    )