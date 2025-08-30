"""
Configuration PROPRE de l'admin Django pour BasicFit v2
Architecture simplifiée avec table unique pour tous les exercices
"""
from django.contrib import admin
from .models import ProgressionMachine
from .models_unified import ExerciceEffectueUnifie, CalendrierEntrainementSimple
from .models_calendar import ExerciceManuel

# ===== ARCHITECTURE SIMPLIFIÉE - SEULEMENT LES MODÈLES ACTIFS =====

@admin.register(ExerciceEffectueUnifie)
class ExerciceEffectueUnifieAdmin(admin.ModelAdmin):
    """
    MODÈLE PRINCIPAL : Table unique pour tous les exercices effectués
    (CSV imports, exercices manuels, temps réel)
    """
    list_display = [
        'utilisateur', 'nom_exercice', 'machine', 'source', 'date_exercice',
        'series_effectuees', 'repetitions_totales', 'poids_utilise', 'volume_total'
    ]
    list_filter = ['source', 'machine__categorie', 'date_exercice']
    search_fields = ['utilisateur__email', 'nom_exercice', 'machine__nom', 'nom_seance']
    date_hierarchy = 'date_exercice'
    ordering = ['-date_exercice', 'nom_exercice']
    
    fieldsets = (
        ('📊 Informations de base', {
            'fields': ('utilisateur', 'source', 'date_exercice')
        }),
        ('🏋️ Exercice', {
            'fields': ('nom_exercice', 'machine', 'nom_seance', 'duree_seance_minutes')
        }),
        ('💪 Performance', {
            'fields': (
                'series_effectuees', 'repetitions_totales', 'poids_utilise',
                'taux_reussite', 'temps_repos_seconde'
            )
        }),
        ('📈 Métriques', {
            'fields': ('volume_total',),
            'classes': ('collapse',)
        }),
        ('📝 Notes & Debug', {
            'fields': ('commentaire_utilisateur', 'ligne_csv_originale'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['volume_total']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur', 'machine')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs

@admin.register(ProgressionMachine)
class ProgressionMachineAdmin(admin.ModelAdmin):
    """
    Progression sur les machines pour l'analyse intelligente
    """
    list_display = [
        'utilisateur', 'machine', 'mode_entrainement', 'poids_actuel',
        'dernier_1rm', 'nombre_seances_machine', 'taux_reussite'
    ]
    list_filter = ['mode_entrainement', 'machine__categorie', 'increment_automatique']
    search_fields = ['utilisateur__email', 'machine__nom']
    ordering = ['utilisateur', 'machine']
    
    fieldsets = (
        ('🎯 Configuration', {
            'fields': ('utilisateur', 'machine', 'mode_entrainement')
        }),
        ('💪 Progression actuelle', {
            'fields': (
                'poids_actuel', 'series_actuelles', 'repetitions_actuelles',
                'dernier_1rm'
            )
        }),
        ('📈 Métriques', {
            'fields': ('nombre_seances_machine', 'progression_poids_total', 'taux_reussite')
        }),
        ('⚙️ Automatisation', {
            'fields': ('increment_automatique', 'seuil_progression'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['nombre_seances_machine', 'progression_poids_total', 'taux_reussite']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur', 'machine', 'mode_entrainement')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs

@admin.register(CalendrierEntrainementSimple)
class CalendrierEntrainementSimpleAdmin(admin.ModelAdmin):
    """
    Métadonnées des séances (surtout pour imports CSV)
    """
    list_display = [
        'utilisateur', 'nom_seance', 'date_entrainement', 'source_donnees',
        'duree_totale_minutes', 'nombre_exercices', 'volume_total_seance'
    ]
    list_filter = ['source_donnees', 'date_entrainement']
    search_fields = ['utilisateur__email', 'nom_seance']
    date_hierarchy = 'date_entrainement'
    ordering = ['-date_entrainement']
    
    fieldsets = (
        ('📅 Séance', {
            'fields': ('utilisateur', 'date_entrainement', 'nom_seance', 'source_donnees')
        }),
        ('📊 Métriques', {
            'fields': ('duree_totale_minutes', 'nombre_exercices', 'volume_total_seance')
        }),
        ('📝 Notes', {
            'fields': ('commentaire',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['nombre_exercices', 'volume_total_seance']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs

@admin.register(ExerciceManuel)
class ExerciceManuelAdmin(admin.ModelAdmin):
    """
    Templates d'exercices créés par l'utilisateur
    """
    list_display = [
        'utilisateur', 'nom_exercice', 'machine', 'est_favori', 
        'nombre_utilisations', 'derniere_utilisation'
    ]
    list_filter = ['est_favori', 'machine__categorie']
    search_fields = ['utilisateur__email', 'nom_exercice']
    ordering = ['-est_favori', '-nombre_utilisations', 'nom_exercice']
    
    fieldsets = (
        ('🏋️ Exercice', {
            'fields': ('utilisateur', 'nom_exercice', 'description', 'machine')
        }),
        ('⚙️ Configuration par défaut', {
            'fields': (
                'series_par_defaut', 'repetitions_par_defaut', 
                'poids_par_defaut', 'repos_par_defaut'
            )
        }),
        ('⭐ Préférences', {
            'fields': ('est_favori', 'groupe_musculaire_cible')
        }),
        ('📊 Statistiques', {
            'fields': ('nombre_utilisations', 'derniere_utilisation'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['nombre_utilisations', 'derniere_utilisation']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur', 'machine')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs

# ===== CONFIGURATION ADMIN =====

admin.site.site_header = "🏋️ BasicFit v2 - Administration"
admin.site.site_title = "BasicFit Admin"
admin.site.index_title = "Gestion des Entraînements"