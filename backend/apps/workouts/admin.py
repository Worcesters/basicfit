"""
Configuration de l'admin Django pour les entraînements BasicFit
"""
from django.contrib import admin
from .models import ProgressionMachine
# SUPPRIMÉ: SeanceEntrainement, ExerciceSeance, SeriExercice (obsolètes)
# SUPPRIMÉ: SeanceSimple (remplacé par les nouveaux modèles)
from .models_refactored import (
    SeanceEffectuee, ExerciceEffectue, SerieEffectuee,
    CalendrierSeance, ExercicePlanifie
)


# ===== ADMINISTRATION DES MODÈLES ACTIFS =====

@admin.register(ProgressionMachine)
class ProgressionMachineAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'machine', 'mode_entrainement', 'poids_actuel',
        'dernier_1rm', 'nombre_seances_machine', 'taux_reussite',
        'derniere_progression'
    ]
    list_filter = [
        'mode_entrainement', 'machine__categorie', 'increment_automatique',
        'derniere_progression', 'premiere_utilisation'
    ]
    search_fields = [
        'utilisateur__email', 'utilisateur__prenom', 'utilisateur__nom',
        'machine__nom'
    ]
    ordering = ['utilisateur', 'machine']

    fieldsets = (
        ('Configuration', {
            'fields': ('utilisateur', 'machine', 'mode_entrainement')
        }),
        ('Progression actuelle', {
            'fields': (
                'poids_actuel', 'series_actuelles', 'repetitions_actuelles',
                'dernier_1rm'
            )
        }),
        ('Historique', {
            'fields': ('derniere_seance', 'nombre_seances_machine')
        }),
        ('Métriques de progression', {
            'fields': (
                'progression_poids_total', 'taux_reussite'
            )
        }),
        ('Configuration automatique', {
            'fields': ('increment_automatique', 'seuil_progression'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('premiere_utilisation', 'derniere_progression'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'premiere_utilisation', 'nombre_seances_machine',
        'progression_poids_total', 'taux_reussite'
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'utilisateur', 'machine', 'mode_entrainement', 'derniere_seance'
        )
        # Filtrage automatique par utilisateur si l'utilisateur n'est pas superuser
        if request.user.is_superuser:
            return qs
        return qs.filter(utilisateur=request.user)


# ===== ADMINISTRATION DES MODÈLES REFACTORISÉS =====

class ExerciceEffectueInline(admin.TabularInline):
    model = ExerciceEffectue
    extra = 0
    fields = ['nom_exercice', 'machine', 'ordre_dans_seance', 'series_realisees', 'repetitions_totales', 'poids_moyen']
    readonly_fields = ['volume_exercice', 'tonnage_exercice']

class SerieEffectueeInline(admin.TabularInline):
    model = SerieEffectuee
    extra = 0
    fields = ['numero_serie', 'repetitions_prevues', 'repetitions_realisees', 'poids_utilise']

class ExercicePlanifieInline(admin.TabularInline):
    model = ExercicePlanifie
    extra = 0
    fields = ['machine', 'ordre_prevu', 'series_prevues', 'repetitions_prevues', 'poids_prevu']

@admin.register(SeanceEffectuee)
class SeanceEffectueeAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'nom', 'date_debut', 'duree_minutes', 'nombre_exercices', 'volume_total']
    list_filter = ['date_debut', 'note_ressenti', 'note_difficulte']
    search_fields = ['utilisateur__email', 'nom', 'commentaire']
    date_hierarchy = 'date_debut'
    ordering = ['-date_debut']
    inlines = [ExerciceEffectueInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs

@admin.register(ExerciceEffectue)
class ExerciceEffectueAdmin(admin.ModelAdmin):
    list_display = ['seance', 'nom_exercice', 'machine', 'series_realisees', 'repetitions_totales', 'poids_moyen', 'taux_reussite']
    list_filter = ['machine__categorie', 'seance__date_debut']
    search_fields = ['nom_exercice', 'machine__nom', 'seance__utilisateur__email']
    ordering = ['-seance__date_debut', 'ordre_dans_seance']
    inlines = [SerieEffectueeInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('seance', 'machine', 'seance__utilisateur')
        if not request.user.is_superuser:
            return qs.filter(seance__utilisateur=request.user)
        return qs

@admin.register(CalendrierSeance)
class CalendrierSeanceAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'nom', 'date_prevue', 'duree_prevue', 'statut', 'mode_entrainement']
    list_filter = ['statut', 'mode_entrainement', 'date_prevue']
    list_editable = ['statut']
    search_fields = ['utilisateur__email', 'nom', 'description']
    date_hierarchy = 'date_prevue'
    ordering = ['-date_prevue']
    inlines = [ExercicePlanifieInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur', 'mode_entrainement')
        if not request.user.is_superuser:
            return qs.filter(utilisateur=request.user)
        return qs