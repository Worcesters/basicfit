"""
Configuration de l'admin Django pour les utilisateurs BasicFit
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ProfilUtilisateur


class ProfilUtilisateurInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profil utilisateur'
    fields = [
        'bio', 'objectifs_personnels', 'blessures_actuelles', 'medicaments',
        'frequence_entrainement_semaine', 'duree_entrainement_moyenne', 'est_public'
    ]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfilUtilisateurInline]

    list_display = [
        'email', 'prenom', 'nom', 'objectif_sportif', 'niveau_experience',
        'est_premium', 'is_active', 'date_joined'
    ]
    list_filter = [
        'objectif_sportif', 'niveau_experience', 'est_premium', 'is_active',
        'est_actif', 'notifications_actives', 'date_joined'
    ]
    list_editable = ['est_premium', 'is_active']
    search_fields = ['email', 'prenom', 'nom', 'username']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'date_naissance')
        }),
        ('Informations physiques', {
            'fields': ('poids', 'taille', 'photo_profil')
        }),
        ('Profil sportif', {
            'fields': (
                'objectif_sportif', 'niveau_experience', 'mode_entrainement_prefere',
                'date_inscription_salle', 'salle_frequentee'
            )
        }),
        ('Préférences', {
            'fields': (
                'notifications_actives', 'notification_rappel_entrainement',
                'notification_progression'
            )
        }),
        ('Statut compte', {
            'fields': ('est_premium', 'est_actif', 'derniere_connexion_app')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'prenom', 'nom', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['derniere_connexion_app', 'last_login', 'date_joined']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mode_entrainement_prefere')


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'frequence_entrainement_semaine', 'duree_entrainement_moyenne',
        'est_public', 'created_at'
    ]
    list_filter = ['est_public', 'frequence_entrainement_semaine', 'created_at']
    list_editable = ['est_public']
    search_fields = ['utilisateur__email', 'utilisateur__prenom', 'utilisateur__nom', 'bio']
    ordering = ['-created_at']

    fieldsets = (
        ('Utilisateur', {
            'fields': ('utilisateur',)
        }),
        ('Informations personnelles', {
            'fields': ('bio', 'objectifs_personnels')
        }),
        ('Santé et limitations', {
            'fields': ('blessures_actuelles', 'medicaments')
        }),
        ('Habitudes d\'entraînement', {
            'fields': ('frequence_entrainement_semaine', 'duree_entrainement_moyenne')
        }),
        ('Paramètres', {
            'fields': ('est_public',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('utilisateur')