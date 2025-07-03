"""
Configuration de l'admin Django pour les machines BasicFit
"""
from django.contrib import admin
from .models import GroupeMusculaire, CategorieMachine, Machine, VarianteMachine


@admin.register(GroupeMusculaire)
class GroupeMusculaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur', 'ordre_affichage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['ordre_affichage', 'is_active']
    search_fields = ['nom', 'description']
    ordering = ['ordre_affichage', 'nom']

    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'couleur', 'icone', 'ordre_affichage', 'is_active')
        }),
    )


@admin.register(CategorieMachine)
class CategorieMachineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'get_nom_display', 'couleur', 'is_active', 'created_at']
    list_filter = ['nom', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['nom', 'description']
    ordering = ['nom']

    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'couleur', 'icone', 'is_active')
        }),
    )


class VarianteMachineInline(admin.TabularInline):
    model = VarianteMachine
    extra = 0
    fields = ['nom', 'description', 'niveau_difficulte', 'is_active']


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'categorie', 'niveau_difficulte', 'popularite',
        'est_disponible', 'poids_minimum', 'poids_maximum', 'created_at'
    ]
    list_filter = [
        'categorie', 'niveau_difficulte', 'est_disponible',
        'necessite_supervision', 'created_at'
    ]
    list_editable = ['est_disponible', 'popularite']
    search_fields = ['nom', 'nom_anglais', 'description', 'tags']
    filter_horizontal = ['groupes_musculaires_primaires', 'groupes_musculaires_secondaires']
    ordering = ['categorie', 'ordre_affichage', 'nom']
    inlines = [VarianteMachineInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'nom_anglais', 'description', 'instructions')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'groupes_musculaires_primaires', 'groupes_musculaires_secondaires')
        }),
        ('Caractéristiques techniques', {
            'fields': ('increment_poids', 'poids_minimum', 'poids_maximum')
        }),
        ('Métadonnées', {
            'fields': ('niveau_difficulte', 'popularite', 'est_disponible', 'necessite_supervision')
        }),
        ('Médias', {
            'fields': ('image_principale', 'video_demonstration'),
            'classes': ('collapse',)
        }),
        ('Informations techniques', {
            'fields': ('fabricant', 'modele', 'numero_serie'),
            'classes': ('collapse',)
        }),
        ('Affichage et tags', {
            'fields': ('ordre_affichage', 'tags'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('nombre_utilisations', 'note_moyenne'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['nombre_utilisations', 'note_moyenne']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categorie')


@admin.register(VarianteMachine)
class VarianteMachineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'machine', 'niveau_difficulte', 'is_active', 'created_at']
    list_filter = ['niveau_difficulte', 'is_active', 'machine__categorie', 'created_at']
    list_editable = ['is_active']
    search_fields = ['nom', 'description', 'machine__nom']
    filter_horizontal = ['groupes_musculaires_specifiques']
    ordering = ['machine', 'nom']

    fieldsets = (
        (None, {
            'fields': ('machine', 'nom', 'description', 'niveau_difficulte')
        }),
        ('Configuration spécifique', {
            'fields': ('groupes_musculaires_specifiques', 'instructions_specifiques', 'is_active')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('machine')