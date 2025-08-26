"""
Configuration de l'admin Django pour les entraînements BasicFit
"""
from django.contrib import admin
from .models import (
    SeanceEntrainement, ExerciceSeance, SeriExercice, ProgressionMachine
)
from .models_simple import SeanceSimple
from .models_refactored import (
    SeanceEffectuee, ExerciceEffectue, SerieEffectuee,
    CalendrierSeance, ExercicePlanifie
)


class SeriExerciceInline(admin.TabularInline):
    model = SeriExercice
    extra = 0
    fields = [
        'numero_serie', 'repetitions_prevues', 'poids_prevu', 'repetitions_realisees',
        'poids_utilise', 'statut', 'note_effort'
    ]
    readonly_fields = []


class ExerciceSeanceInline(admin.TabularInline):
    model = ExerciceSeance
    extra = 0
    fields = [
        'ordre_dans_seance', 'machine', 'series_prevues', 'repetitions_prevues',
        'poids_prevu', 'statut', 'nombre_series'
    ]
    readonly_fields = ['volume_total', 'tonnage_total']


@admin.register(SeanceEntrainement)
class SeanceEntrainementAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'nom', 'mode_entrainement', 'date_prevue',
        'statut', 'duree_prevue', 'note_ressenti', 'nombre_exercices'
    ]
    list_filter = [
        'statut', 'mode_entrainement', 'date_prevue', 'note_ressenti',
        'note_difficulte', 'created_at'
    ]
    list_editable = ['statut']
    search_fields = [
        'utilisateur__email', 'utilisateur__prenom', 'utilisateur__nom',
        'nom', 'description', 'commentaire'
    ]
    date_hierarchy = 'date_prevue'
    ordering = ['-date_prevue']
    inlines = [ExerciceSeanceInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'mode_entrainement', 'nom', 'description')
        }),
        ('Planning', {
            'fields': ('date_prevue', 'duree_prevue', 'statut')
        }),
        ('Réalisation', {
            'fields': ('date_debut', 'date_fin', 'commentaire'),
            'classes': ('collapse',)
        }),
        ('Évaluation', {
            'fields': ('note_ressenti', 'note_difficulte'),
            'classes': ('collapse',)
        }),
        ('Métriques physiques', {
            'fields': (
                'poids_utilisateur', 'frequence_cardiaque_repos',
                'frequence_cardiaque_max'
            ),
            'classes': ('collapse',)
        }),
        ('Données calculées', {
            'fields': (
                'volume_total', 'tonnage_total', 'nombre_exercices',
                'nombre_series_totales'
            ),
            'classes': ('collapse',)
        }),
        ('Contexte', {
            'fields': ('salle', 'partenaire_entrainement', 'temperature'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'volume_total', 'tonnage_total', 'nombre_exercices', 'nombre_series_totales'
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'utilisateur', 'mode_entrainement'
        )
        # Filtrage automatique par utilisateur si l'utilisateur n'est pas superuser
        if request.user.is_superuser:
            return qs
        return qs.filter(utilisateur=request.user)


@admin.register(ExerciceSeance)
class ExerciceSeanceAdmin(admin.ModelAdmin):
    list_display = [
        'seance_user', 'seance', 'machine', 'ordre_dans_seance', 'series_prevues',
        'poids_prevu', 'statut', 'nombre_series', 'volume_total'
    ]
    list_filter = [
        'statut', 'machine__categorie', 'seance__mode_entrainement',
        'seance__utilisateur', 'created_at'
    ]
    list_editable = ['statut']
    search_fields = [
        'seance__nom', 'machine__nom', 'seance__utilisateur__email',
        'commentaire'
    ]
    ordering = ['seance__date_prevue', 'ordre_dans_seance']
    inlines = [SeriExerciceInline]
    
    # Filtrage automatique par utilisateur si l'utilisateur n'est pas superuser
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'seance', 'machine', 'variante', 'seance__utilisateur'
        )
        if request.user.is_superuser:
            return qs
        return qs.filter(seance__utilisateur=request.user)
    
    def seance_user(self, obj):
        """Affiche l'utilisateur de la séance"""
        return obj.seance.utilisateur.email
    seance_user.short_description = 'Utilisateur'
    seance_user.admin_order_field = 'seance__utilisateur__email'

    fieldsets = (
        ('Configuration', {
            'fields': (
                'seance', 'machine', 'variante', 'ordre_dans_seance', 'statut'
            )
        }),
        ('Planification', {
            'fields': (
                'series_prevues', 'repetitions_prevues', 'duree_prevue',
                'poids_prevu', 'repos_prevu'
            )
        }),
        ('Résultats', {
            'fields': (
                'nombre_series', 'repetitions_realisees', 'duree_realisee',
                'poids_utilise'
            )
        }),
        ('Métriques', {
            'fields': (
                'volume_total', 'tonnage_total', 'charge_maximale_theorique'
            ),
            'classes': ('collapse',)
        }),
        ('Évaluation', {
            'fields': ('duree_totale', 'note_ressenti', 'commentaire'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['volume_total', 'tonnage_total', 'charge_maximale_theorique']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'seance', 'machine', 'variante'
        )


@admin.register(SeriExercice)
class SeriExerciceAdmin(admin.ModelAdmin):
    list_display = [
        'serie_user', 'exercice', 'numero_serie', 'repetitions_prevues', 'duree_prevue',
        'poids_prevu', 'repetitions_realisees', 'duree_realisee',
        'poids_utilise', 'statut', 'note_effort'
    ]
    list_filter = [
        'statut', 'note_effort', 'exercice__machine__categorie', 
        'exercice__seance__utilisateur', 'created_at'
    ]
    list_editable = ['statut']
    search_fields = [
        'exercice__machine__nom', 'exercice__seance__nom',
        'exercice__seance__utilisateur__email', 'commentaire'
    ]
    ordering = ['exercice__seance__date_prevue', 'exercice__ordre_dans_seance', 'numero_serie']
    
    def serie_user(self, obj):
        """Affiche l'utilisateur de la série"""
        return obj.exercice.seance.utilisateur.email
    serie_user.short_description = 'Utilisateur'
    serie_user.admin_order_field = 'exercice__seance__utilisateur__email'

    fieldsets = (
        ('Configuration', {
            'fields': ('exercice', 'numero_serie', 'statut')
        }),
        ('Planification', {
            'fields': ('repetitions_prevues', 'duree_prevue', 'poids_prevu', 'repos_prevu')
        }),
        ('Résultats', {
            'fields': ('repetitions_realisees', 'duree_realisee', 'poids_utilise', 'repos_reel')
        }),
        ('Métriques', {
            'fields': ('duree_serie', 'frequence_cardiaque_apres', 'note_effort'),
            'classes': ('collapse',)
        }),
        ('Commentaire', {
            'fields': ('commentaire',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'exercice__machine', 'exercice__seance', 'exercice__seance__utilisateur'
        )
        # Filtrage automatique par utilisateur si l'utilisateur n'est pas superuser
        if request.user.is_superuser:
            return qs
        return qs.filter(exercice__seance__utilisateur=request.user)


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


@admin.register(SeanceSimple)
class SeanceSimpleAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'machine_nom', 'date_seance', 'type_exercice', 
        'duree_minutes', 'note_ressenti', 'created_at'
    ]
    list_filter = [
        'type_exercice', 'date_seance', 'note_ressenti', 'created_at'
    ]
    list_editable = ['type_exercice', 'duree_minutes', 'note_ressenti']
    search_fields = [
        'utilisateur__email', 'utilisateur__prenom', 'utilisateur__nom',
        'machine_nom', 'commentaire'
    ]
    date_hierarchy = 'date_seance'
    ordering = ['-date_seance', 'machine_nom']

    fieldsets = (
        ('Séance CSV', {
            'fields': ('utilisateur', 'machine_nom', 'date_seance', 'type_exercice')
        }),
        ('Détails optionnels', {
            'fields': ('duree_minutes', 'note_ressenti', 'commentaire'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('utilisateur')
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